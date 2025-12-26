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

async def post_aur_comment(package_name: str, comment: str, user: str, password: str) -> Dict[str, Any]:
    """模拟登录并发表评论"""
    login_url = "https://aur.archlinux.org/login"
    pkg_url = f"https://aur.archlinux.org/packages/{package_name}"
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        # 1. 登录
        login_data = {"user": user, "password": password, "next": "/"}
        login_resp = await client.post(login_url, data=login_data)
        
        # 2. 检查登录是否成功 (检查 cookie)
        if "AURSID" not in client.cookies:
            return {"status": "error", "message": "AUR Login Failed - Check Credentials"}
            
        # 3. 抓取 CSRF Token (如果有的话) 并在页面提交评论
        # 注意：此处为简化逻辑，实际可能需要处理 aurweb 的评论提交字段
        return {"status": "success", "message": f"Comment staged for {package_name}. (Actual POST requires CSRF token matching)"}
