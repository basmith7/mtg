"""Small JSON-over-HTTP helper with retry on rate limits."""
import json
import time
import urllib.error
import urllib.request

BROWSER_UA = 'Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0'


def request(method, url, body=None, headers=None, retries=8, backoff=5):
    """Return parsed JSON ({} for empty bodies, {'_raw': ...} for non-JSON). Retries HTTP 429."""
    hdrs = {'User-Agent': BROWSER_UA, 'Accept': 'application/json', **(headers or {})}
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        hdrs.setdefault('Content-Type', 'application/json')
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, data=data, headers=hdrs, method=method)) as resp:
                raw = resp.read()
            if not raw:
                return {}
            try:
                return json.loads(raw)
            except ValueError:
                return {'_raw': raw[:200].decode(errors='replace')}
        except urllib.error.HTTPError as e:
            if e.code != 429 or attempt == retries - 1:
                raise
            time.sleep(backoff * (attempt + 1))


def get(url, **kw):
    return request('GET', url, **kw)
