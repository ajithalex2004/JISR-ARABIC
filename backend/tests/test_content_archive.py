import io
import os
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.errors import ApplicationError
from backend.modules.curriculum.content_archive import install_content_archive


def make_archive(entries):
    """entries: list of (name, bytes | None for dir | ('symlink', target))."""
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
        for name, payload in entries:
            info = tarfile.TarInfo(name)
            if payload is None:
                info.type = tarfile.DIRTYPE
                archive.addfile(info)
            elif isinstance(payload, tuple):
                info.type = tarfile.SYMTYPE
                info.linkname = payload[1]
                archive.addfile(info)
            else:
                info.size = len(payload)
                archive.addfile(info, io.BytesIO(payload))
    buffer.seek(0)
    return buffer


class TestContentArchive(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.env = patch.dict(os.environ, {"FAHIM_CONTENT_DIR": self.tmp.name})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def test_installs_pages_under_requested_root(self):
        archive = make_archive([("moe_gr5_vol1_2023", None), ("moe_gr5_vol1_2023/page_7.png", b"png-bytes")])
        result = install_content_archive("pdf_pages_sample", archive)
        self.assertEqual(result["files_installed"], 1)
        self.assertEqual((Path(self.tmp.name) / "pdf_pages_sample/moe_gr5_vol1_2023/page_7.png").read_bytes(), b"png-bytes")
        self.assertFalse(list(Path(self.tmp.name).glob("*.part")))

    def test_rejects_unknown_root(self):
        with self.assertRaises(ApplicationError) as ctx:
            install_content_archive("backend", make_archive([("a.png", b"x")]))
        self.assertEqual(ctx.exception.status_code, 400)

    def test_rejects_path_traversal(self):
        with self.assertRaises(ApplicationError):
            install_content_archive("pdf_pages_sample", make_archive([("../escape.png", b"x")]))
        self.assertFalse((Path(self.tmp.name) / "escape.png").exists())

    def test_rejects_symlinks_and_disallowed_types(self):
        with self.assertRaises(ApplicationError):
            install_content_archive("pdf_pages_sample", make_archive([("link.png", ("symlink", "/etc/passwd"))]))
        with self.assertRaises(ApplicationError):
            install_content_archive("vision-output-new", make_archive([("run.sh", b"echo hi")]))

    def test_rejects_oversized_upload(self):
        with patch.dict(os.environ, {"FAHIM_CONTENT_UPLOAD_MAX_MB": "0"}):
            with self.assertRaises(ApplicationError) as ctx:
                install_content_archive("pdf_pages_sample", make_archive([("a.png", b"x")]))
        self.assertEqual(ctx.exception.status_code, 413)

    def test_rejects_non_archive(self):
        with self.assertRaises(ApplicationError):
            install_content_archive("pdf_pages_sample", io.BytesIO(b"not a tar file"))


class TestContentArchiveEndpoint(unittest.TestCase):
    def test_requires_admin(self):
        from fastapi.testclient import TestClient
        from backend.main import app
        client = TestClient(app)
        res = client.post("/api/admin/content-archive?root=pdf_pages_sample",
                          files={"file": ("a.tgz", b"x", "application/gzip")})
        self.assertEqual(res.status_code, 401)


if __name__ == "__main__":
    unittest.main()
