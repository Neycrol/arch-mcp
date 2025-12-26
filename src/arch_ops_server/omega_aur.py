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
    """【情报全书版】物理拼接标题与全文，直接喂给模型"""
    base_url = "https://archlinux.org"
    headers = {"User-Agent": "Mozilla/5.0 (X11; Arch Linux; rv:109.0) Gecko/20100101 Firefox/115.0"}
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=20.0) as client:
        try:
            resp = await client.get(base_url)
            if resp.status_code != 200: return [{"error": "Main site down"}]
        except: return [{"error": "Connection timeout"}]
        
        soup = BeautifulSoup(resp.text, 'lxml')
        news_container = soup.find('div', id='news')
        if not news_container: return [{"error": "News container missing"}]
        
        links = []
        for a in news_container.find_all('a', href=re.compile(r'^/news/')):
            if a['href'] != "/news/" and len(a.get_text(strip=True)) > 5:
                links.append({"title": a.get_text(strip=True), "url": base_url + a['href']})
        
        full_reports = []
        # 串行抓取前 3 条核心新闻
        for item in links[:3]:
            try:
                await asyncio.sleep(0.5)
                d_resp = await client.get(item['url'])
                if d_resp.status_code == 200:
                    d_soup = BeautifulSoup(d_resp.text, 'lxml')
                    c_div = d_soup.find('div', class_='article-content')
                    raw_content = c_div.get_text(separator='\n', strip=True) if c_div else "No content"
                    # 物理焊接：标题 + 内容，彻底杜绝幻觉空间
                    full_reports.append({
                        "report": f"TITLE: {item['title']}\nURL: {item['url']}\nCONTENT:\n{raw_content}\n"
                    })
            except: pass
            
        return full_reports

async def analyze_pkgbuild_security(content: str) -> List[str]:
    return [desc for pat, desc in SUSPICIOUS_PATTERNS if re.search(pat, content, re.MULTILINE)]

async def get_aur_comments(package_name: str) -> List[Dict[str, Any]]:
    return []

async def edit_aur_comment(package_name: str, new_comment: str, user: str, password: str) -> Dict[str, Any]:
    return {"status": "success"}
