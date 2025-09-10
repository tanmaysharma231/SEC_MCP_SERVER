from aiolimiter import AsyncLimiter

# SEC guidance is 10 requests per second per IP. Stay under it.
GLOBAL_LIMITER = AsyncLimiter(max_rate=8, time_period=1.0)
HOST_LIMITERS = {}


