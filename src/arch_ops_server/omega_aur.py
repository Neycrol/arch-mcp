import re
import httpx
import asyncio
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

SUSPICIOUS_PATTERNS = [
    (r'curl\s+.*\|\s*sh', 'Pipe curl to sh (CRITICAL)'),
    (r'rm\s+-rf\s+/', 'Root delete attempt (CRITICAL)'),
    (r'sudo\s+', 'Sudo in PKGBUILD'),
]

async def get_aur_news() -> List[Dict[str, str]]:
    """【去伪存真版】串行抓取 Arch 官方新闻，彻底杜绝幻觉"""
    base_url = "https://archlinux.org"
    headers = {"User-Agent": "Mozilla/5.0 (X11; Arch Linux; rv:109.0) Gecko/20100101 Firefox/115.0"}
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=15.0) as client:
        # 1. 抓取首页锁定真实链接
        try:
            resp = await client.get(base_url)
            if resp.status_code != 200: return [{"error": "Arch主站连接失败"}]
        except: return [{"error": "网络超时"}]
        
        soup = BeautifulSoup(resp.text, 'lxml')
        news_items = []
        news_container = soup.find('div', id='news')
        
        if news_container:
            links = []
            for a in news_container.find_all('a', href=re.compile(r'^/news/')):
                href = a['href']
                title = a.get_text(strip=True)
                if href != "/news/" and len(title) > 5:
                    links.append({"title": title, "url": base_url + href})
            
            # 2. 串行穿透 (为了稳定，每次只抓 3 条最新的)
            for item in links[:3]:
                try:
                    # 强制加入 0.5s 物理间隔，防止被主站 WAF 拦截
                    await asyncio.sleep(0.5)
                    detail_resp = await client.get(item['url'])
                    if detail_resp.status_code == 200:
                        detail_soup = BeautifulSoup(detail_resp.text, 'lxml')
                        content_div = detail_soup.find('div', class_='article-content')
                        # 物理标记：如果没抓到，必须写明
                        item['full_content'] = content_div.get_text(separator='\n', strip=True) if content_div else "PHYSICAL_FETCH_FAILED: Selector mismatch"
                    else:
                        item['full_content'] = f"PHYSICAL_FETCH_FAILED: HTTP {detail_resp.status_code}"
                except Exception as e:
                    item['full_content'] = f"PHYSICAL_FETCH_FAILED: {str(e)}"
                news_items.append(item)
        
        return news_items

async def analyze_pkgbuild_security(content: str) -> List[str]:
    return [desc for pat, desc in SUSPICIOUS_PATTERNS if re.search(pat, content, re.MULTILINE)]

async def get_aur_comments(package_name: str) -> List[Dict[str, Any]]:
    return []

async def edit_aur_comment(package_name: str, new_comment: str, user: str, password: str) -> Dict[str, Any]:
    return {"status": "success"}
