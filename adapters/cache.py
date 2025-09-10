import hashlib, json, time, os, pathlib

class SimpleTTLCache:
    def __init__(self, base_dir=".cache"):
        self.base_dir = pathlib.Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _key(self, name: str, params: dict) -> str:
        m = hashlib.sha256()
        m.update(name.encode())
        m.update(json.dumps(params, sort_keys=True).encode())
        return m.hexdigest()

    def get(self, name: str, params: dict, ttl_seconds: int):
        key = self._key(name, params)
        fp = self.base_dir / key
        if not fp.exists():
            return None
        try:
            raw = json.loads(fp.read_text())
            if time.time() - raw["ts"] > ttl_seconds:
                return None
            return raw["data"]
        except Exception:
            return None

    def set(self, name: str, params: dict, data):
        key = self._key(name, params)
        fp = self.base_dir / key
        fp.write_text(json.dumps({"ts": time.time(), "data": data}))
        return True


