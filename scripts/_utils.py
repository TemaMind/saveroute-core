import requests, time, hashlib
from 00_config import RAW
def download(url: str, fname: str | None = None) -> str:
    t0 = time.time()
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    if not fname:
        ext = url.split(".")[-1].split("?")[0]
        stamp = time.strftime("%Y%m%d")
        fname = f"{fname or hashlib.md5(url.encode()).hexdigest()}_{stamp}.{ext}"
    path = RAW / fname
    path.write_bytes(resp.content)
    print(f"⬇ downloaded {fname} ({len(resp.content)/1024:.1f} KB, {time.time()-t0:.1f}s)")
    return str(path)