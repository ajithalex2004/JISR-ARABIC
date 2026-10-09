"""
Cloud & Local Storage Abstraction Layer for JISR Arabic.
Provides seamless, unified object storage support across:
1. Local filesystem (development, local testing, single-node Docker)
2. Amazon S3 / Cloudflare R2 / MinIO (multi-instance, high-concurrency cloud production)

Used by curriculum audio synthesis, textbook PDF ingestion, and background task artifacts.
"""
import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger("fahim.storage")


class StorageAdapter:
    """Base interface for all storage providers."""

    def upload_file(self, local_path: str, remote_key: str, content_type: str = "audio/mpeg") -> str:
        raise NotImplementedError

    def upload_bytes(self, data: bytes, remote_key: str, content_type: str = "audio/mpeg") -> str:
        raise NotImplementedError

    def file_exists(self, remote_key: str) -> bool:
        raise NotImplementedError

    def get_url(self, remote_key: str) -> str:
        raise NotImplementedError

    def download_file(self, remote_key: str, local_path: str) -> bool:
        raise NotImplementedError


class LocalStorageAdapter(StorageAdapter):
    """Local disk filesystem storage adapter."""

    def __init__(self, root_dir: Optional[str] = None):
        self.root_dir = Path(root_dir or os.getenv("FAHIM_AUDIO_CACHE_DIR", os.path.join("tmp", "audio-cache"))).resolve()
        self.root_dir.mkdir(parents=True, exist_ok=True)

    def _resolve_path(self, remote_key: str) -> Path:
        filename = Path(remote_key).name
        return self.root_dir / filename

    def upload_file(self, local_path: str, remote_key: str, content_type: str = "audio/mpeg") -> str:
        dest = self._resolve_path(remote_key)
        if Path(local_path).resolve() != dest.resolve():
            import shutil
            shutil.copy2(local_path, dest)
        return self.get_url(remote_key)

    def upload_bytes(self, data: bytes, remote_key: str, content_type: str = "audio/mpeg") -> str:
        dest = self._resolve_path(remote_key)
        dest.write_bytes(data)
        return self.get_url(remote_key)

    def file_exists(self, remote_key: str) -> bool:
        return self._resolve_path(remote_key).is_file()

    def get_url(self, remote_key: str) -> str:
        filename = Path(remote_key).name
        return f"/api/audio/cache/{filename}"

    def download_file(self, remote_key: str, local_path: str) -> bool:
        src = self._resolve_path(remote_key)
        if src.is_file():
            import shutil
            shutil.copy2(src, local_path)
            return True
        return False


class S3StorageAdapter(StorageAdapter):
    """
    AWS S3 / Cloudflare R2 / MinIO compatible object storage adapter.
    Enables multi-instance stateless pods to share media assets and serve from a CDN.
    """

    def __init__(
        self,
        bucket_name: Optional[str] = None,
        region_name: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        cdn_domain: Optional[str] = None,
        prefix: str = "audio/",
    ):
        self.bucket_name = bucket_name or os.getenv("S3_BUCKET_NAME", "jisr-audio-production")
        self.region_name = region_name or os.getenv("S3_REGION_NAME", os.getenv("AWS_DEFAULT_REGION", "me-central-1"))
        self.endpoint_url = endpoint_url or os.getenv("S3_ENDPOINT_URL")
        self.cdn_domain = cdn_domain or os.getenv("S3_CDN_DOMAIN")
        self.prefix = prefix or os.getenv("S3_AUDIO_PREFIX", "audio/")
        self.local_cache = LocalStorageAdapter()
        self._client = None

    def _get_client(self):
        if self._client is not None:
            return self._client
        try:
            import boto3
            from botocore.config import Config

            cfg = Config(
                region_name=self.region_name,
                retries={"max_attempts": 3, "mode": "standard"},
                signature_version="s3v4"
            )
            client_kwargs = {"config": cfg}
            if self.endpoint_url:
                client_kwargs["endpoint_url"] = self.endpoint_url
            if os.getenv("AWS_ACCESS_KEY_ID") and os.getenv("AWS_SECRET_ACCESS_KEY"):
                client_kwargs["aws_access_key_id"] = os.getenv("AWS_ACCESS_KEY_ID")
                client_kwargs["aws_secret_access_key"] = os.getenv("AWS_SECRET_ACCESS_KEY")
            elif os.getenv("S3_ACCESS_KEY_ID") and os.getenv("S3_SECRET_ACCESS_KEY"):
                client_kwargs["aws_access_key_id"] = os.getenv("S3_ACCESS_KEY_ID")
                client_kwargs["aws_secret_access_key"] = os.getenv("S3_SECRET_ACCESS_KEY")

            self._client = boto3.client("s3", **client_kwargs)
            return self._client
        except ImportError:
            logger.warning("boto3 is not installed. S3StorageAdapter operating in fallback mode.")
            return None
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            return None

    def _full_key(self, remote_key: str) -> str:
        key = remote_key.lstrip("/")
        if not key.startswith(self.prefix):
            key = f"{self.prefix}{key}"
        return key

    def upload_file(self, local_path: str, remote_key: str, content_type: str = "audio/mpeg") -> str:
        # Keep local copy cached for immediate fast reads
        self.local_cache.upload_file(local_path, remote_key, content_type)
        client = self._get_client()
        if client:
            full_key = self._full_key(remote_key)
            try:
                client.upload_file(
                    Filename=local_path,
                    Bucket=self.bucket_name,
                    Key=full_key,
                    ExtraArgs={"ContentType": content_type, "CacheControl": "public, max-age=31536000, immutable"}
                )
                logger.info(f"Uploaded {full_key} to s3://{self.bucket_name}")
            except Exception as e:
                logger.error(f"S3 upload_file failed for {full_key}: {e}")
        return self.get_url(remote_key)

    def upload_bytes(self, data: bytes, remote_key: str, content_type: str = "audio/mpeg") -> str:
        self.local_cache.upload_bytes(data, remote_key, content_type)
        client = self._get_client()
        if client:
            full_key = self._full_key(remote_key)
            try:
                client.put_object(
                    Bucket=self.bucket_name,
                    Key=full_key,
                    Body=data,
                    ContentType=content_type,
                    CacheControl="public, max-age=31536000, immutable"
                )
                logger.info(f"Uploaded bytes for {full_key} to s3://{self.bucket_name}")
            except Exception as e:
                logger.error(f"S3 put_object failed for {full_key}: {e}")
        return self.get_url(remote_key)

    def file_exists(self, remote_key: str) -> bool:
        if self.local_cache.file_exists(remote_key):
            return True
        client = self._get_client()
        if client:
            full_key = self._full_key(remote_key)
            try:
                client.head_object(Bucket=self.bucket_name, Key=full_key)
                return True
            except Exception:
                return False
        return False

    def get_url(self, remote_key: str) -> str:
        filename = Path(remote_key).name
        full_key = self._full_key(filename)
        if self.cdn_domain:
            domain = self.cdn_domain.rstrip("/")
            if not domain.startswith("http://") and not domain.startswith("https://"):
                domain = f"https://{domain}"
            return f"{domain}/{full_key}"
        if self.bucket_name:
            return f"https://{self.bucket_name}.s3.{self.region_name}.amazonaws.com/{full_key}"
        return f"/api/audio/cache/{filename}"

    def download_file(self, remote_key: str, local_path: str) -> bool:
        if self.local_cache.download_file(remote_key, local_path):
            return True
        client = self._get_client()
        if client:
            full_key = self._full_key(remote_key)
            try:
                client.download_file(Bucket=self.bucket_name, Key=full_key, Filename=local_path)
                return True
            except Exception as e:
                logger.error(f"S3 download_file failed for {full_key}: {e}")
        return False


_global_adapter: Optional[StorageAdapter] = None


def get_storage_adapter() -> StorageAdapter:
    """Retrieve singleton storage adapter based on STORAGE_BACKEND setting."""
    global _global_adapter
    if _global_adapter is not None:
        return _global_adapter
    backend = os.getenv("STORAGE_BACKEND", "local").lower()
    if backend == "s3":
        _global_adapter = S3StorageAdapter()
    else:
        _global_adapter = LocalStorageAdapter()
    return _global_adapter


def reset_storage_adapter():
    """Reset adapter instance (useful for testing configuration switches)."""
    global _global_adapter
    _global_adapter = None
