import httpx, asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
from urllib.parse import urlparse
from .rate_limit import GLOBAL_LIMITER, HOST_LIMITERS
from .cache import SimpleTTLCache

CACHE = SimpleTTLCache()

def host_limiter(url: str):
    host = urlparse(url).netloc
    lim = HOST_LIMITERS.get(host)
    if not lim:
        from aiolimiter import AsyncLimiter
        lim = AsyncLimiter(2, 1.0)
        HOST_LIMITERS[host] = lim
    return lim

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=0.3, max=2))
async def fetch_json(url: str, cache_key: str, cache_ttl: int):
    cached = CACHE.get(cache_key, {"url": url}, cache_ttl)
    if cached is not None:
        return cached

    async with GLOBAL_LIMITER:
        async with host_limiter(url):
            async with httpx.AsyncClient(timeout=15.0, http2=True) as client:
                resp = await client.get(url, headers={"User-Agent": "sec-mcp/0.1 contact@example.com"})
                resp.raise_for_status()
                data = resp.json()
                CACHE.set(cache_key, {"url": url}, data)
                return data


