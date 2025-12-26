import re
import httpx
import asyncio
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

SUSPICIOUS_PATTERNS = [
    (r'curl\s+.*\|\s*sh', 'Pipe curl to sh (CRITICAL)'),
    (r'rm\s+-rf\s+/', 'Root delete attempt (CRITICAL)'),
]

async def get_aur_news() -> List[Dict[str, str]]:
    """物理抓取 Arch Linux 官方新闻并生成全书报告"""
    base_url = "https://archlinux.org"
    headers = {"User-Agent": "Mozilla/5.0 (X11; Arch Linux; rv:109.0) Gecko/20100101 Firefox/115.0"}
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=20.0) as client:
        try:
            resp = await client.get(base_url)
            if resp.status_code != 200: return [{"error": "Main site unreachable"}]
            soup = BeautifulSoup(resp.text, 'lxml')
            news_container = soup.find('div', id='news')
            if not news_container: return [{"error": "News box not found"}]
            
            links = []
            for a in news_container.find_all('a', href=re.compile(r'^/news/')):
                if a['href'] != "/news/" and len(a.get_text(strip=True)) > 5:
                    links.append({"title": a.get_text(strip=True), "url": base_url + a['href']})
            
            reports = []
            for item in links[:3]:
                await asyncio.sleep(0.5)
                d_resp = await client.get(item['url'])
                if d_resp.status_code == 200:
                    c_div = BeautifulSoup(d_resp.text, 'lxml').find('div', class_='article-content')
                    content = c_div.get_text(separator='\n', strip=True) if c_div else "No content"
                    reports.append({"report": f"TITLE: {item['title']}\nURL: {item['url']}\nCONTENT:\n{content}\n"})
            return reports
        except: return [{"error": "Scraping sequence failed"}]

async def analyze_pkgbuild_security(content: str) -> List[str]:
    return [desc for pat, desc in SUSPICIOUS_PATTERNS if re.search(pat, content, re.MULTILINE)]

async def get_aur_comments(package_name: str) -> List[Dict[str, Any]]:
    url = f"https://aur.archlinux.org/packages/{package_name}"
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            r = await client.get(url)
            s = BeautifulSoup(r.text, 'lxml')
            return [{"content": d.get_text(strip=True), "author": "AUR User"} for d in s.find_all('div', class_='article-content')][:5]
        except: return []

def generate_aur_comment_link(package_name: str) -> str:
    """物理生成评论传送门 (补齐缺失的函数)"""
    return f"https://aur.archlinux.org/packages/{package_name}#add-comment"
