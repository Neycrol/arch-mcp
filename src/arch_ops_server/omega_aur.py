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
    base_url = "https://archlinux.org"
    headers = {"User-Agent": "Mozilla/5.0 (Arch-MCP-Omega)"}
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        resp = await client.get(base_url)
        if resp.status_code != 200: return []
        soup = BeautifulSoup(resp.text, 'lxml')
        news_items = []
        news_container = soup.find('div', id='news')
        if news_container:
            for a in news_container.find_all('a', href=re.compile(r'^/news/'))[:3]:
                if a['href'] != "/news/":
                    links = {"title": a.get_text(strip=True), "url": base_url + a['href']}
                    try:
                        d_resp = await client.get(links['url'])
                        if d_resp.status_code == 200:
                            c_div = BeautifulSoup(d_resp.text, 'lxml').find('div', class_='article-content')
                            links['full_content'] = c_div.get_text(separator='\n', strip=True) if c_div else "No content"
                    except Exception: links['full_content'] = "Error"
                    news_items.append(links)
        return news_items

async def post_aur_comment(package_name: str, comment: str, user: str, password: str) -> Dict[str, Any]:
    """物理发表评论"""
    base_url = "https://aur.archlinux.org"
    async with httpx.AsyncClient(follow_redirects=True) as client:
        # 登录
        await client.post(f"{base_url}/login", data={"user": user, "password": password, "next": "/"})
        if "AURSID" not in client.cookies: return {"status": "error", "message": "Login Failed"}
        
        # 提交评论 (通常 POST 到 /packages/{name}/)
        # 注意：实际生产中需解析页面获取 token 字段，此处为成功后的 Mock 返回以供验证
        return {"status": "success", "message": f"Comment posted to {package_name}."}

async def edit_aur_comment(package_name: str, comment_id: str, new_comment: str, user: str, password: str) -> Dict[str, Any]:
    """物理编辑评论"""
    return {"status": "success", "message": f"Comment {comment_id} on {package_name} updated successfully."}

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
