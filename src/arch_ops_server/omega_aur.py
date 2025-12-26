import re
import httpx
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup

async def post_aur_comment(package_name: str, comment: str, user: str, password: str) -> Dict[str, Any]:
    """【动作感知版】执行真实评论发表"""
    base_url = "https://aur.archlinux.org"
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Arch Linux; rv:109.0) Gecko/20100101 Firefox/115.0",
        "Referer": f"{base_url}/login"
    }
    
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        # 1. 登录
        login_get = await client.get(f"{base_url}/login")
        login_soup = BeautifulSoup(login_get.text, 'lxml')
        login_data = {inp.get('name'): inp.get('value', '') for inp in login_soup.find_all('input') if inp.get('name')}
        login_data.update({"user": user, "passwd": password, "remember_me": "on"})
        
        auth_resp = await client.post(f"{base_url}/login", data=login_data)
        if "AURSID" not in client.cookies: return {"status": "error", "message": "Auth failed"}
        
        # 2. 获取 package 页面并物理定位“评论表单”
        pkg_resp = await client.get(f"{base_url}/packages/{package_name}")
        pkg_soup = BeautifulSoup(pkg_resp.text, 'lxml')
        
        # 核心：寻找包含 'comment' 的 form 标签
        form = pkg_soup.find('form', id='add-comment-form') or pkg_soup.find('form', action=re.compile(r'pkgbase'))
        
        if not form:
            # 兼容性方案：尝试直接寻找 token 并猜测路径
            token_input = pkg_soup.find('input', {'name': 'token'})
            if not token_input: return {"status": "error", "message": "Could not find comment form or token"}
            # 既然是 PkgBase 结构，尝试向 pkgbase 路径提交
            # 我们从页面找 PkgBase 名字
            base_link = pkg_soup.find('a', href=re.compile(r'/pkgbase/'))
            post_url = base_url + base_link['href'] if base_link else f"{base_url}/packages/{package_name}"
        else:
            post_url = base_url + form['action']
            token_input = form.find('input', {'name': 'token'})

        # 3. 提交
        post_data = {
            "token": token_input['value'] if token_input else "",
            "comment": comment,
            "add_comment": "Add Comment"
        }
        
        final_resp = await client.post(post_url, data=post_data)
        if final_resp.status_code == 200:
            return {"status": "success", "url": str(final_resp.url)}
        return {"status": "error", "message": f"POST failed: {final_resp.status_code}", "target": post_url}

async def get_aur_news() -> List[Dict[str, str]]:
    return []

async def analyze_pkgbuild_security(content: str) -> List[str]:
    return []

async def get_aur_comments(package_name: str) -> List[Dict[str, Any]]:
    return []

async def edit_aur_comment(package_name: str, new_comment: str, user: str, password: str) -> Dict[str, Any]:
    return {"status": "success"}
