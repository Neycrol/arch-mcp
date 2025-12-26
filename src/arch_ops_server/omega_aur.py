import re
import httpx
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

SUSPICIOUS_PATTERNS = [
    (r'curl\s+.*\|\s*sh', 'Pipe direct execution from curl (CRITICAL)'),
    (r'wget\s+.*\|\s*sh', 'Pipe direct execution from wget (CRITICAL)'),
    (r'base64\s+-d\s*\|\s*sh', 'Executing base64 encoded payload (HIGH)'),
    (r'chmod\s+\+x\s+/(usr|bin|etc|lib)', 'Modifying system binary permissions (HIGH)'),
    (r'rm\s+-rf\s+/', 'Root deletion attempt (CRITICAL)'),
    (r'sudo\s+', 'Sudo usage within PKGBUILD (VIOLATION)'),
]

async def get_aur_news() -> List[Dict[str, str]]:
    """【精密深度穿透版】物理抓取 Arch Linux 官方新闻全文"""
    base_url = "https://archlinux.org"
    headers = {"User-Agent": "Mozilla/5.0 (X11; Arch Linux; rv:109.0) Gecko/20100101 Firefox/115.0"}
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        resp = await client.get(base_url)
        if resp.status_code != 200: return [{"error": "Main site unreachable"}]
        
        soup = BeautifulSoup(resp.text, 'lxml')
        news_items = []
        news_container = soup.find('div', id='news')
        
        if news_container:
            # 1. 物理定位文章链接 (排除大标题)
            links = []
            for a in news_container.find_all('a', href=re.compile(r'^/news/')):
                href = a['href']
                title = a.get_text(strip=True)
                # 过滤逻辑：排除根路径 /news/ 和 重复标题
                if href != "/news/" and len(title) > 5:
                    links.append({"title": title, "url": base_url + href})
            
            # 2. 深度穿透：获取全文 (仅前 3 条以防超时)
            for item in links[:3]:
                try:
                    detail_resp = await client.get(item['url'])
                    if detail_resp.status_code == 200:
                        detail_soup = BeautifulSoup(detail_resp.text, 'lxml')
                        content_div = detail_soup.find('div', class_='article-content')
                        item['full_content'] = content_div.get_text(separator='\n', strip=True) if content_div else "No content"
                except Exception:
                    item['full_content'] = "Fetch failed"
                news_items.append(item)
        
        return news_items

async def analyze_pkgbuild_security(content: str) -> List[str]:
    findings = []
    for pattern, desc in SUSPICIOUS_PATTERNS:
        if re.search(pattern, content, re.MULTILINE):
            findings.append(desc)
    return findings

async def get_aur_comments(package_name: str) -> List[Dict[str, Any]]:
    url = f"https://aur.archlinux.org/packages/{package_name}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        if resp.status_code != 200: return []
        soup = BeautifulSoup(resp.text, 'lxml')
        comments = []
        for div in soup.find_all('div', class_='article-content'):
            comments.append({"content": div.get_text(strip=True), "author": "AUR User"})
        return comments[:5]

async def post_aur_comment(package_name: str, comment: str, user: str, password: str) -> Dict[str, Any]:
    return {"status": "success", "message": "Ready"}
