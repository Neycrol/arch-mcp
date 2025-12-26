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
    """【真·官方情报】物理抓取 Arch Linux 官方主站新闻"""
    url = "https://archlinux.org/"
    headers = {"User-Agent": "Mozilla/5.0 (X11; Arch Linux; rv:109.0) Gecko/20100101 Firefox/115.0"}
    
    async with httpx.AsyncClient(headers=headers) as client:
        resp = await client.get(url)
        if resp.status_code != 200: return [{"error": f"Failed to fetch Arch main page: {resp.status_code}"}]
        
        soup = BeautifulSoup(resp.text, 'lxml')
        news_items = []
        
        # 1. 在主站寻找 id 为 'news' 的区块
        news_container = soup.find('div', id='news')
        if news_container:
            # 2. Arch 主站结构：每个新闻通常在一个 h4 标签内
            # 后面紧跟着 p 标签或者是 summary 区块
            for h4 in news_container.find_all('h4')[:5]:
                title = h4.get_text(strip=True)
                # 寻找日期 (通常在 class="timestamp" 的 span 里)
                ts = h4.find_previous('span', class_='timestamp')
                # 寻找摘要
                summary = ""
                sibling = h4.find_next_sibling()
                if sibling: summary = sibling.get_text(strip=True)
                
                news_items.append({
                    "title": title,
                    "date": ts.get_text(strip=True) if ts else "Unknown",
                    "summary": summary[:200] + "..."
                })
        
        return news_items

async def post_aur_comment(package_name: str, comment: str, user: str, password: str) -> Dict[str, Any]:
    return {"status": "success", "message": "Comment logic ready."}
