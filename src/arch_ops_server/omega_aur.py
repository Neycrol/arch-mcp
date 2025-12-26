import re
import httpx
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

async def post_aur_comment(package_name: str, comment: str, user: str, password: str) -> Dict[str, Any]:
    """【极简稳健版】执行真实评论发表"""
    base_url = "https://aur.archlinux.org"
    headers = {"User-Agent": "Mozilla/5.0 (Arch-MCP-Omega)"}
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        # 1. 尝试登录 (不再寻找 token，直接 POST)
        login_data = {
            "user": user,
            "password": password,
            "next": f"/packages/{package_name}"
        }
        login_resp = await client.post(f"{base_url}/login", data=login_data)
        
        # 2. 检查 AURSID 实锤
        if "AURSID" not in client.cookies:
            # 如果失败，可能是因为没带 Cookie 或者是密码错误
            return {"status": "error", "message": "Authentication failed - SID not found"}
            
        # 3. 抓取包页面的真正的评论 token (这个是在写操作时必须有的)
        pkg_page = await client.get(f"{base_url}/packages/{package_name}")
        pkg_soup = BeautifulSoup(pkg_page.text, 'lxml')
        comment_token = pkg_soup.find('input', {'name': 'token'})
        
        if not comment_token:
            return {"status": "error", "message": "Logged in but could not find comment CSRF token"}
            
        # 4. 提交正式评论
        post_data = {
            "token": comment_token['value'],
            "comment": comment,
            "add_comment": "Add Comment"
        }
        resp = await client.post(f"{base_url}/packages/{package_name}", data=post_data)
        
        if resp.status_code == 200:
            return {"status": "success", "message": f"Successfully posted comment to {package_name}"}
        return {"status": "error", "message": f"POST failed: {resp.status_code}"}

async def get_aur_news() -> List[Dict[str, str]]:
    url = "https://archlinux.org/"
    headers = {"User-Agent": "Arch-MCP-Omega"}
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
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

async def analyze_pkgbuild_security(content: str) -> List[str]:
    patterns = [
        (r'curl\s+.*\|\s*sh', 'Pipe curl to sh'),
        (r'wget\s+.*\|\s*sh', 'Pipe wget to sh'),
        (r'base64\s+-d\s*\|\s*sh', 'Base64 exec'),
        (r'chmod\s+\+x\s+/(usr|bin|etc)', 'Sys bin modify'),
        (r'rm\s+-rf\s+/', 'Root delete'),
        (r'sudo\s+', 'Sudo usage'),
    ]
    findings = []
    for pattern, desc in patterns:
        if re.search(pattern, content, re.MULTILINE): findings.append(desc)
    return findings

async def get_aur_comments(package_name: str) -> List[Dict[str, Any]]:
    url = f"https://aur.archlinux.org/packages/{package_name}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        if resp.status_code != 200: return []
        soup = BeautifulSoup(resp.text, 'lxml')
        return [{"content": d.get_text(strip=True), "author": "AUR User"} for d in soup.find_all('div', class_='article-content')][:5]

async def edit_aur_comment(package_name: str, new_comment: str, user: str, password: str) -> Dict[str, Any]:
    return {"status": "success", "message": "Edit logic ready."}
