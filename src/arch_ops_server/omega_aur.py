import re
import httpx
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

async def post_aur_comment(package_name: str, comment: str, aursid: str) -> Dict[str, Any]:
    """【物理越迁版】利用现有 AURSID 直接发表评论"""
    base_url = "https://aur.archlinux.org"
    # 注入物理指纹
    cookies = {"AURSID": aursid}
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Arch Linux; rv:109.0) Gecko/20100101 Firefox/115.0",
        "Referer": f"{base_url}/packages/{package_name}",
        "Origin": base_url
    }
    
    async with httpx.AsyncClient(headers=headers, cookies=cookies, follow_redirects=True) as client:
        # 1. 物理直达包页面抓取 Token
        pkg_resp = await client.get(f"{base_url}/packages/{package_name}")
        if pkg_resp.status_code != 200:
            return {"status": "error", "message": f"Cannot reach package page: {pkg_resp.status_code}"}
            
        soup = BeautifulSoup(pkg_resp.text, 'lxml')
        
        # 检查是否真的登录成功 (寻找 Logout 链接)
        if not soup.find('a', href=re.compile(r'/logout/')):
            return {"status": "error", "message": "Cookie expired or invalid. Logout link not found."}
            
        # 2. 抓取全量表单字段
        form = soup.find('form', id='add-comment-form')
        if not form:
            return {"status": "error", "message": "Could not find comment form. Check package base permissions."}
            
        post_data = {inp.get('name'): inp.get('value', '') for inp in form.find_all('input') if inp.get('name')}
        post_data.update({
            "comment": comment,
            "add_comment": "Add Comment"
        })
        
        # 3. 物理执行最终提交
        resp = await client.post(f"{base_url}/packages/{package_name}", data=post_data)
        
        if resp.status_code == 200 and "Comment added" in resp.text:
            return {"status": "success", "message": f"Successfully posted to {package_name}"}
        return {"status": "error", "message": "POST successful but confirmation missing in response."}

async def get_aur_news() -> List[Dict[str, str]]:
    url = "https://archlinux.org/"
    async with httpx.AsyncClient(headers={"User-Agent": "Arch-Omega"}, follow_redirects=True) as client:
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
    patterns = [(r'curl\s+.*\|\s*sh', 'Pipe curl'), (r'rm\s+-rf\s+/', 'Root delete')]
    return [desc for pat, desc in patterns if re.search(pat, content, re.MULTILINE)]

async def get_aur_comments(package_name: str) -> List[Dict[str, Any]]:
    url = f"https://aur.archlinux.org/packages/{package_name}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        if resp.status_code != 200: return []
        soup = BeautifulSoup(resp.text, 'lxml')
        return [{"content": d.get_text(strip=True), "author": "AUR User"} for d in soup.find_all('div', class_='article-content')][:5]
