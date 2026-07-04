import os


def _int_env(name: str, fallback: str) -> int:
    return int(os.getenv(f"TUF_{name}", os.getenv(name, fallback)))


class CacheRateLimitSettings:
    redis_url = os.getenv("TUF_REDIS_URL", os.getenv("REDIS_URL"))
    upstash_redis_rest_url = os.getenv("UPSTASH_REDIS_REST_URL")
    upstash_redis_rest_token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
    cache_ttl_seconds = _int_env("API_CACHE_TTL_SECONDS", "3600")
    invalid_user_cache_ttl_seconds = _int_env("INVALID_USER_CACHE_TTL_SECONDS", "300")
    rate_limit_ip_requests = _int_env("RATE_LIMIT_IP_REQUESTS", "60")
    rate_limit_handle_requests = _int_env("RATE_LIMIT_HANDLE_REQUESTS", "30")
    rate_limit_window_seconds = _int_env("RATE_LIMIT_WINDOW_SECONDS", "60")
    invalid_rate_limit_ip_requests = _int_env("INVALID_RATE_LIMIT_IP_REQUESTS", "10")
    invalid_rate_limit_handle_requests = _int_env("INVALID_RATE_LIMIT_HANDLE_REQUESTS", "5")
    invalid_rate_limit_window_seconds = _int_env("INVALID_RATE_LIMIT_WINDOW_SECONDS", "600")
    rate_limit_backoff_base_seconds = _int_env("RATE_LIMIT_BACKOFF_BASE_SECONDS", "5")
    rate_limit_backoff_max_seconds = _int_env("RATE_LIMIT_BACKOFF_MAX_SECONDS", "300")


cache_rate_limit_settings = CacheRateLimitSettings()
