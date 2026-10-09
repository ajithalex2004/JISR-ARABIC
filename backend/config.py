"""Deployment configuration validation. Secret values are never logged or returned."""
import os

class ConfigurationError(RuntimeError):
    pass

def validate_deployment_config() -> None:
    env = os.getenv("FAHIM_ENV", "development").lower()
    if env != "production":
        return
    required = ("DATABASE_URL", "FAHIM_SECRET_KEY", "FAHIM_PAYMENT_WEBHOOK_SECRET", "FAHIM_CORS_ORIGINS", "FAHIM_PAYMENT_PROVIDER")
    missing = [name for name in required if not os.getenv(name, "").strip()]
    if missing:
        raise ConfigurationError("Missing required production configuration: " + ", ".join(missing))
    if len(os.environ["FAHIM_SECRET_KEY"].strip()) < 32:
        raise ConfigurationError("FAHIM_SECRET_KEY must be at least 32 characters in production")
    if len(os.environ["FAHIM_PAYMENT_WEBHOOK_SECRET"].strip()) < 24:
        raise ConfigurationError("FAHIM_PAYMENT_WEBHOOK_SECRET must be at least 24 characters in production")
    if os.environ["DATABASE_URL"].strip().lower().startswith("sqlite"):
        raise ConfigurationError("Production deployments must use a managed PostgreSQL DATABASE_URL; SQLite is development-only")
    if os.getenv("FAHIM_SEED_DEMO", "0") == "1":
        raise ConfigurationError("FAHIM_SEED_DEMO must be disabled in production")
    if any(origin.strip() == "*" for origin in os.environ["FAHIM_CORS_ORIGINS"].split(",")):
        raise ConfigurationError("FAHIM_CORS_ORIGINS cannot contain wildcard '*' in production")
    redis_url = os.getenv("REDIS_URL", "").strip()
    if redis_url and not (redis_url.startswith("redis://") or redis_url.startswith("rediss://")):
        raise ConfigurationError("REDIS_URL must use redis:// or rediss:// protocol")
    if os.getenv("FAHIM_PAYMENT_PROVIDER", "").lower() not in ("stripe", "paypal"):
        raise ConfigurationError("FAHIM_PAYMENT_PROVIDER must be stripe or paypal in production")
