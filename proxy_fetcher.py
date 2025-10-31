import asyncio
import aiohttp
import requests
from bs4 import BeautifulSoup
from typing import List

SOURCES = [
    "https://www.proxy-list.download/api/v1/get?type=http",
    "https://www.proxy-list.download/api/v1/get?type=https",
    "https://free-proxy-list.net/",
]

async def test_proxy(session: aiohttp.ClientSession, proxy: str, timeout=8) -> bool:
    proxy_url = f"http://{proxy}" if not proxy.startswith('http') else proxy
    try:
        async with session.get('http://httpbin.org/ip', proxy=proxy_url, timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False

async def filter_working_proxies(proxies: List[str], concurrency: int = 50) -> List[str]:
    connector = aiohttp.TCPConnector(limit_per_host=concurrency)
    timeout = aiohttp.ClientTimeout(total=12)
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = [asyncio.create_task(test_proxy(session, p)) for p in proxies]
        results = await asyncio.gather(*tasks)
    return [p for p, ok in zip(proxies, results) if ok]

def fetch_from_plaintext_url(url: str) -> List[str]:
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        text = r.text
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        proxies = [l for l in lines if ':' in l and l.split(':')[0].replace('.', '').isdigit()]
        return proxies
    except Exception:
        return []

def fetch_from_free_proxy_list(url: str) -> List[str]:
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find("table", id="proxylisttable")
        proxies = []
        if table and table.tbody:
            for row in table.tbody.find_all("tr"):
                cols = row.find_all("td")
                ip = cols[0].text.strip()
                port = cols[1].text.strip()
                proxies.append(f"{ip}:{port}")
        return proxies
    except Exception:
        return []

def fetch_all_sources() -> List[str]:
    proxies = []
    for src in SOURCES:
        if 'free-proxy-list.net' in src:
            proxies.extend(fetch_from_free_proxy_list(src))
        else:
            proxies.extend(fetch_from_plaintext_url(src))
    seen = set(); out = []
    for p in proxies:
        if p not in seen:
            seen.add(p); out.append(p)
    return out

if __name__ == '__main__':
    print('Fetching proxies...')
    allp = fetch_all_sources()
    print(f'Found {len(allp)} candidate proxies. Testing top 50...')
    ok = asyncio.run(filter_working_proxies(allp[:200]))
    print(f'Working: {len(ok)}')
    for p in ok:
        print(p)
