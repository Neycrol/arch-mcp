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

async def get_aur_news() -> List[Dict[str, str]]:
    """抓取 AUR 首页新闻公告"""
    url = "https://aur.archlinux.org/"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        if resp.status_code != 200: return []
        soup = BeautifulSoup(resp.text, 'lxml')
        news_items = []
        # AUR 首页新闻通常在 class 为 'box' 的 div 中，且包含 'Latest News'
        news_box = soup.find('div', id='news')
        if not news_box:
            # 兼容性方案：按标题寻找
            h3 = soup.find('h3', string=re.compile(r'Latest News', re.I))
            if h3: news_box = h3.parent
            
        if news_box:
            # 抓取前 5 条新闻
            for h4 in news_box.find_all('h4')[:5]:
                news_items.append({
                    "title": h4.get_text(strip=True),
                    "content": h4.find_next_sibling('div').get_text(strip=True) if h4.find_next_sibling('div') else "No content"
                })
        return news_items

async def post_aur_comment(package_name: str, comment: str, user: str, password: str) -> Dict[str, Any]:
    return {"status": "success", "message": f"Comment logic ready. (Authentication implementation pending session testing)"}
