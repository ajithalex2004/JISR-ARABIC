"""Install textbook scan / OCR archives onto the content volume (FAHIM_CONTENT_DIR).

Used to seed a hosted deployment from the folders on a developer PC
(scripts/upload_content.py sends one .tar.gz per edition folder).
"""
import os
import shutil
import tarfile
import tempfile
from pathlib import PurePosixPath
from typing import BinaryIO

from backend.config import content_root
from backend.errors import ApplicationError

CONTENT_ROOTS = ("pdf_pages_sample", "vision-output-new", "vision-output")
ALLOWED_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".json", ".txt"}
_CHUNK = 1024 * 1024


def _max_upload_bytes() -> int:
    return int(os.getenv("FAHIM_CONTENT_UPLOAD_MAX_MB", "1024")) * 1024 * 1024


def _safe_members(archive: tarfile.TarFile):
    """Yield only plain files and folders with relative, allowed-type paths."""
    for member in archive.getmembers():
        path = PurePosixPath(member.name)
        if path.is_absolute() or ".." in path.parts:
            raise ApplicationError(400, f"Unsafe path in archive: {member.name}")
        if member.isdir():
            yield member
        elif member.isfile():
            if path.suffix.lower() not in ALLOWED_SUFFIXES:
                raise ApplicationError(400, f"File type not allowed in archive: {member.name}")
            yield member
        else:
            raise ApplicationError(400, f"Links and special files are not allowed: {member.name}")


def install_content_archive(root: str, stream: BinaryIO) -> dict:
    if root not in CONTENT_ROOTS:
        raise ApplicationError(400, f"root must be one of: {', '.join(CONTENT_ROOTS)}")
    target = content_root() / root
    target.mkdir(parents=True, exist_ok=True)

    limit = _max_upload_bytes()
    received = 0
    with tempfile.NamedTemporaryFile(dir=content_root(), suffix=".tgz.part") as staged:
        while chunk := stream.read(_CHUNK):
            received += len(chunk)
            if received > limit:
                raise ApplicationError(413, f"Archive exceeds {limit // (1024 * 1024)} MB; split it into smaller parts")
            staged.write(chunk)
        staged.flush()
        staged.seek(0)
        try:
            with tarfile.open(fileobj=staged, mode="r:*") as archive:
                members = list(_safe_members(archive))
                archive.extractall(path=target, members=members, filter="data")
        except tarfile.TarError as exc:
            raise ApplicationError(400, f"Not a valid tar archive: {exc}")

    files = sum(1 for m in members if m.isfile())
    free_bytes = shutil.disk_usage(target).free
    return {"root": root, "files_installed": files, "bytes_received": received, "volume_free_mb": free_bytes // (1024 * 1024)}
