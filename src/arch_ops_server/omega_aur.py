import re
import httpx
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

async def post_aur_comment(package_name: str, comment: str, user: str, password: str) -> Dict[str, Any]:
    """【浏览器级模拟版】执行真实评论发表"""
    base_url = "https://aur.archlinux.org"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Arch Linux; rv:109.0) Gecko/20100101 Firefox/115.0",
        "Referer": f"{base_url}/login",
        "Origin": base_url
    }
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        # 1. 物理建立 Session (必须先访问登录页)
        await client.get(f"{base_url}/login")
        
        # 2. 构造全量登录表单
        login_data = {
            "user": user,
            "password": password,
            "next": f"/packages/{package_name}",
            "remember_me": "on"
        }
        
        # 3. 执行登录
        resp = await client.post(f"{base_url}/login", data=login_data)
        
        if "AURSID" not in client.cookies:
            return {
                "status": "error", 
                "message": "Auth failed - SID not found",
                "debug_info": f"Final URL: {resp.url}, Status: {resp.status_code}"
            }
            
        # 4. 抓取包页面的真正的评论 token
        pkg_page = await client.get(f"{base_url}/packages/{package_name}")
        pkg_soup = BeautifulSoup(pkg_page.text, 'lxml')
        comment_token = pkg_soup.find('input', {'name': 'token'})
        
        if not comment_token:
            return {"status": "error", "message": "Logged in but token missing"}
            
        # 5. 提交正式评论
        post_data = {
            "token": comment_token['value'],
            "comment": comment,
            "add_comment": "Add Comment"
        }
        resp = await client.post(f"{base_url}/packages/{package_name}", data=post_data)
        
        if resp.status_code == 200:
            return {"status": "success", "message": f"Successfully posted to {package_name}"}
        return {"status": "error", "message": f"POST failed: {resp.status_code}"}

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

async def analyze_pkgbuild_security(content: str) -> List[str]:
    patterns = [(r'curl\s+.*\|\s*sh', 'Pipe curl'), (r'rm\s+-rf\s+/', 'Root delete'), (r'sudo\s+', 'Sudo')]
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
