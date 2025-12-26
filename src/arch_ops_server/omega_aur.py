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
        if re.search(pattern, content, re.MULTILINE): findings.append(desc)
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
    """【物理穿透版】带双重 Token 的登录与评论逻辑"""
    base_url = "https://aur.archlinux.org"
    headers = {"User-Agent": "Mozilla/5.0 (Arch-MCP-Omega)"}
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        # 1. 抓取登录页面的 CSRF Token
        login_page = await client.get(f"{base_url}/login")
        login_soup = BeautifulSoup(login_page.text, 'lxml')
        login_token = login_soup.find('input', {'name': 'token'})
        
        if not login_token:
            return {"status": "error", "message": "Could not find login CSRF token"}
            
        # 2. 执行带 Token 的登录
        login_data = {
            "user": user,
            "password": password,
            "token": login_token['value'],
            "next": f"/packages/{package_name}"
        }
        await client.post(f"{base_url}/login", data=login_data)
        
        if "AURSID" not in client.cookies:
            return {"status": "error", "message": "Authentication failed - Check Credentials"}
            
        # 3. 抓取包页面的评论 CSRF Token
        pkg_page = await client.get(f"{base_url}/packages/{package_name}")
        pkg_soup = BeautifulSoup(pkg_page.text, 'lxml')
        comment_token = pkg_soup.find('input', {'name': 'token'})
        
        if not comment_token:
            return {"status": "error", "message": "Could not find comment CSRF token"}
            
        # 4. 提交正式评论
        post_data = {
            "token": comment_token['value'],
            "comment": comment,
            "add_comment": "Add Comment"
        }
        resp = await client.post(f"{base_url}/packages/{package_name}", data=post_data)
        
        if resp.status_code == 200 and "Comment added" in resp.text:
            return {"status": "success", "message": f"Comment successfully posted to {package_name}"}
        return {"status": "success", "note": "POST sent, but result text unclear. Check AUR page."}

async def get_aur_news() -> List[Dict[str, str]]:
    url = "https://archlinux.org/"
    async with httpx.AsyncClient(headers={"User-Agent": "Arch-MCP-Omega"}, follow_redirects=True) as client:
        resp = await client.get(url)
        if resp.status_code != 200: return []
        soup = BeautifulSoup(resp.text, 'lxml')
        news = []
        news_container = soup.find('div', id='news')
        if news_container:
            for a in news_container.find_all('a', href=re.compile(r'^/news/'))[:3]:
                if a['href'] != "/news/":
                    try:
                        d = await client.get("https://archlinux.org" + a['href'])
                        c = BeautifulSoup(d.text, 'lxml').find('div', class_='article-content')
                        news.append({"title": a.get_text(strip=True), "full_content": c.get_text(strip=True)})
                    except: pass
        return news
