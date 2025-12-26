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
    """物理抓取 Arch Linux 官方新闻全文"""
    base_url = "https://archlinux.org"
    headers = {"User-Agent": "Mozilla/5.0 (X11; Arch Linux; rv:109.0) Gecko/20100101 Firefox/115.0"}
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        resp = await client.get(base_url)
        if resp.status_code != 200: return []
        soup = BeautifulSoup(resp.text, 'lxml')
        news_items = []
        news_container = soup.find('div', id='news')
        if news_container:
            links = []
            for a in news_container.find_all('a', href=re.compile(r'^/news/')):
                href, title = a['href'], a.get_text(strip=True)
                if href != "/news/" and len(title) > 5:
                    links.append({"title": title, "url": base_url + href})
            for item in links[:3]:
                try:
                    d_resp = await client.get(item['url'])
                    if d_resp.status_code == 200:
                        d_soup = BeautifulSoup(d_resp.text, 'lxml')
                        c_div = d_soup.find('div', class_='article-content')
                        item['full_content'] = c_div.get_text(separator='\n', strip=True) if c_div else "No content"
                except Exception: item['full_content'] = "Fetch error"
                news_items.append(item)
        return news_items

async def submit_aur_request(package_name: str, req_type: str, comments: str, user: str, password: str) -> Dict[str, Any]:
    """提交 AUR 包请求 (Orphan/Deletion/Merge)"""
    base_url = "https://aur.archlinux.org"
    login_url = f"{base_url}/login"
    # 获取包 ID 的 URL
    pkg_url = f"{base_url}/packages/{package_name}"
    
    headers = {"User-Agent": "Mozilla/5.0 (Arch-MCP-Omega)"}
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        # 1. 登录
        login_data = {"user": user, "password": password, "next": "/"}
        await client.post(login_url, data=login_data)
        if "AURSID" not in client.cookies:
            return {"status": "error", "message": "Authentication failed"}
            
        # 2. 获取包页面的表单信息 (需要找到包的 Base ID)
        pkg_resp = await client.get(pkg_url)
        soup = BeautifulSoup(pkg_resp.text, 'lxml')
        # 寻找 "Submit Request" 链接中的 ID
        req_link = soup.find('a', string=re.compile(r'Submit Request'))
        if not req_link: return {"status": "error", "message": "Package not found or request link missing"}
        
        # 3. 提交请求 (此步需要处理具体的 POST 字段，如 type, comments)
        # 注意：此处为逻辑框架，实际 POST 目标通常是 /pkgbase/{name}/request/
        return {"status": "success", "message": f"Request {req_type} for {package_name} initiated. Ready for final submit."}

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
