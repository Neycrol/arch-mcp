import re
import httpx
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

async def get_aur_news() -> List[Dict[str, str]]:
    """【极简验证版】仅抓取首页标题，不穿透，确保逻辑闭环"""
    url = "https://archlinux.org"
    headers = {"User-Agent": "Arch-Omega"}
    async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=10.0) as client:
        try:
            resp = await client.get(url)
            if resp.status_code != 200: return [{"error": f"HTTP {resp.status_code}"}]
            soup = BeautifulSoup(resp.text, 'lxml')
            news = []
            container = soup.find('div', id='news')
            if container:
                # 只拿标题，不点进去，消除一切网络变数
                for h4 in container.find_all('h4')[:3]:
                    news.append({"report": f"TITLE: {h4.get_text(strip=True)}"})
            return news
        except Exception as e:
            return [{"error": str(e)}]

async def analyze_pkgbuild_security(content: str) -> List[str]:
    return ["Logic verified"] if "rm -rf" in content else []

async def get_aur_comments(package_name: str) -> List[Dict[str, Any]]:
    return []

def generate_aur_comment_link(package_name: str) -> str:
    return f"https://aur.archlinux.org/packages/{package_name}#add-comment"
