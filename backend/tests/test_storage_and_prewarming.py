"""
Unit tests for S3 storage adapter, CDN URL routing, and audio pre-warming engine.
"""
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
from fastapi.testclient import TestClient

from backend.main import app
from backend.storage import (
    LocalStorageAdapter, S3StorageAdapter,
    get_storage_adapter, reset_storage_adapter
)
from backend.modules.curriculum.audio import synthesize_audio
from backend.scripts.prewarm_audio import (
    collect_curriculum_phrases, extract_phrases_from_lesson, run_prewarming
)


class TestStorageAndPrewarming(unittest.TestCase):
    def setUp(self):
        reset_storage_adapter()
        self.temp_dir = tempfile.mkdtemp()
        self.client = TestClient(app)

    def tearDown(self):
        reset_storage_adapter()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_local_storage_adapter_crud(self):
        """LocalStorageAdapter correctly uploads, checks existence, and downloads files."""
        adapter = LocalStorageAdapter(root_dir=self.temp_dir)
        test_file = Path(self.temp_dir) / "source.mp3"
        test_file.write_bytes(b"ID3_MOCK_AUDIO_DATA")

        # Upload
        url = adapter.upload_file(str(test_file), "mock_123.mp3")
        self.assertEqual(url, "/api/audio/cache/mock_123.mp3")
        self.assertTrue(adapter.file_exists("mock_123.mp3"))

        # Download
        dest = Path(self.temp_dir) / "downloaded.mp3"
        success = adapter.download_file("mock_123.mp3", str(dest))
        self.assertTrue(success)
        self.assertEqual(dest.read_bytes(), b"ID3_MOCK_AUDIO_DATA")

    def test_s3_storage_adapter_cdn_url_generation(self):
        """S3StorageAdapter formats CDN and direct S3 bucket URLs properly."""
        # 1. Custom CDN domain configured
        adapter_cdn = S3StorageAdapter(
            bucket_name="jisr-audio-bucket",
            region_name="me-central-1",
            cdn_domain="https://cdn.jisr.ae",
            prefix="curriculum/audio/"
        )
        url_cdn = adapter_cdn.get_url("lesson_01.mp3")
        self.assertEqual(url_cdn, "https://cdn.jisr.ae/curriculum/audio/lesson_01.mp3")

        # 2. Direct S3 bucket URL (no custom CDN)
        adapter_s3 = S3StorageAdapter(
            bucket_name="jisr-audio-bucket",
            region_name="me-central-1",
            cdn_domain=None,
            prefix="audio/"
        )
        url_s3 = adapter_s3.get_url("lesson_01.mp3")
        self.assertEqual(url_s3, "https://jisr-audio-bucket.s3.me-central-1.amazonaws.com/audio/lesson_01.mp3")

    def test_s3_storage_adapter_upload_mock(self):
        """S3StorageAdapter interacts with boto3 client when available."""
        adapter = S3StorageAdapter(bucket_name="test-bucket", region_name="me-central-1")
        mock_boto = MagicMock()
        adapter._client = mock_boto

        test_file = Path(self.temp_dir) / "sample.mp3"
        test_file.write_bytes(b"AUDIO_BYTES")

        adapter.upload_file(str(test_file), "sample.mp3")
        mock_boto.upload_file.assert_called_once()
        call_kwargs = mock_boto.upload_file.call_args[1]
        self.assertEqual(call_kwargs["Bucket"], "test-bucket")
        self.assertEqual(call_kwargs["Key"], "audio/sample.mp3")

    def test_storage_adapter_factory_switching(self):
        """get_storage_adapter returns S3StorageAdapter when STORAGE_BACKEND=s3."""
        with patch.dict(os.environ, {"STORAGE_BACKEND": "s3", "S3_BUCKET_NAME": "prod-bucket"}):
            reset_storage_adapter()
            adapter = get_storage_adapter()
            self.assertIsInstance(adapter, S3StorageAdapter)
            self.assertEqual(adapter.bucket_name, "prod-bucket")

        with patch.dict(os.environ, {"STORAGE_BACKEND": "local"}):
            reset_storage_adapter()
            adapter = get_storage_adapter()
            self.assertIsInstance(adapter, LocalStorageAdapter)

    def test_audio_route_redirects_to_cdn_when_file_in_s3(self):
        """GET /api/audio/cache/{filename} redirects (307) to CDN URL when file is in cloud storage."""
        with patch.dict(os.environ, {
            "STORAGE_BACKEND": "s3",
            "S3_CDN_DOMAIN": "cdn.jisr-arabic.com",
            "FAHIM_AUDIO_CACHE_DIR": self.temp_dir
        }):
            reset_storage_adapter()
            adapter = get_storage_adapter()
            # Mock file_exists to return True
            with patch.object(adapter, "file_exists", return_value=True):
                resp = self.client.get("/api/audio/cache/remote_clip_999.mp3", follow_redirects=False)
                self.assertEqual(resp.status_code, 307)
                self.assertEqual(resp.headers.get("location"), "https://cdn.jisr-arabic.com/audio/remote_clip_999.mp3")

    def test_collect_curriculum_phrases_and_prewarming_dry_run(self):
        """Pre-warming script scans curriculum lessons and completes dry run accurately."""
        phrases = collect_curriculum_phrases(grades=[5], terms=[1])
        self.assertGreater(len(phrases), 50)
        self.assertTrue(any("ألعاب الكرة" in p for p in phrases))

        stats = run_prewarming(grades=[5], terms=[1], limit=10, dry_run=True)
        self.assertEqual(stats["total_targeted"], 10)
        self.assertEqual(stats["newly_synthesized"], 0)
        self.assertEqual(stats["failed"], 0)


if __name__ == "__main__":
    unittest.main()
