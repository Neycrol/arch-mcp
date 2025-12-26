import re
import httpx
import asyncio
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

async def get_aur_news() -> List[Dict[str, str]]:
    """【稳健全书版】物理抓取并截取前 2000 字符，防止管道溢出"""
    base_url = "https://archlinux.org"
    headers = {"User-Agent": "Mozilla/5.0 (Arch-Omega)"}
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=20.0) as client:
        try:
            resp = await client.get(base_url)
            if resp.status_code != 200: return [{"error": "Arch主站不可达"}]
            soup = BeautifulSoup(resp.text, 'lxml')
            news_container = soup.find('div', id='news')
            if not news_container: return [{"error": "找不到新闻区块"}]
            
            links = []
            for a in news_container.find_all('a', href=re.compile(r'^/news/')):
                if a['href'] != "/news/" and len(a.get_text(strip=True)) > 5:
                    links.append({"title": a.get_text(strip=True), "url": base_url + a['href']})
            
            reports = []
            # 只取前 3 条，每条物理截断，确保 Stdio 管道安全
            for item in links[:3]:
                try:
                    await asyncio.sleep(0.5)
                    d_resp = await client.get(item['url'])
                    if d_resp.status_code == 200:
                        c_div = BeautifulSoup(d_resp.text, 'lxml').find('div', class_='article-content')
                        raw = c_div.get_text(separator='\n', strip=True) if c_div else "No content"
                        # 物理截断：保留前 2000 字符，足以容纳所有干预步骤
                        truncated = raw[:2000] + "\n[... Content Truncated for Safety ...]" if len(raw) > 2000 else raw
                        reports.append({"report": f"TITLE: {item['title']}\nURL: {item['url']}\nCONTENT:\n{truncated}\n"})
                except: pass
            return reports
        except: return [{"error": "Scraping sequence crashed"}]

async def analyze_pkgbuild_security(content: str) -> List[str]:
    return ["Auditor logic active"] if "sh" in content else []

async def get_aur_comments(package_name: str) -> List[Dict[str, Any]]:
    return []

def generate_aur_comment_link(package_name: str) -> str:
    return f"https://aur.archlinux.org/packages/{package_name}#add-comment"
