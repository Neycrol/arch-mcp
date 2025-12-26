import re
import httpx
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

async def get_aur_news() -> List[Dict[str, str]]:
    """物理抓取 Arch Linux 官方新闻"""
    url = "https://archlinux.org/"
    async with httpx.AsyncClient(headers={"User-Agent": "Arch-Omega"}, follow_redirects=True) as client:
        resp = await client.get(url)
        if resp.status_code != 200: return []
        soup = BeautifulSoup(resp.text, 'lxml')
        news = []
        container = soup.find('div', id='news')
        if container:
            for a in container.find_all('a', href=re.compile(r'^/news/'))[:3]:
                if a['href'] != "/news/":
                    try:
                        d = await client.get("https://archlinux.org" + a['href'])
                        c = BeautifulSoup(d.text, 'lxml').find('div', class_='article-content')
                        news.append({"title": a.get_text(strip=True), "content": c.get_text(strip=True)})
                    except: pass
        return news

async def analyze_pkgbuild_security(content: str) -> List[str]:
    """安全审计逻辑"""
    patterns = [(r'curl\s+.*\|\s*sh', 'Pipe curl'), (r'rm\s+-rf\s+/', 'Root delete')]
    return [desc for pat, desc in patterns if re.search(pat, content, re.MULTILINE)]

def generate_aur_comment_link(package_name: str) -> str:
    """生成直接指向评论区的传送门"""
    return f"https://aur.archlinux.org/packages/{package_name}#add-comment"

async def get_aur_comments(package_name: str) -> List[Dict[str, Any]]:
    """获取现有评论"""
    url = f"https://aur.archlinux.org/packages/{package_name}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        if resp.status_code != 200: return []
        soup = BeautifulSoup(resp.text, 'lxml')
        return [{"content": d.get_text(strip=True), "author": "AUR User"} for d in soup.find_all('div', class_='article-content')][:5]
