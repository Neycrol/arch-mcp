import sys
import os
import json
import asyncio
import logging
from pathlib import Path

# --- [物理禁言：彻底解决 Stdio 协议污染] ---
# 必须在所有 import 之前执行！强制将 root logger 重定向到 stderr
logging.basicConfig(
    level=logging.WARNING, 
    stream=sys.stderr,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 1. 物理自感知
current_file = Path(__file__).resolve()
src_dir = str(current_file.parent.parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

# 2. 初始化奥米加影子服务器
server = Server("aur-omega")

@server.list_tools()
async def list_tools():
    return [
        Tool(name="get_aur_news", description="Fetch full Arch Linux news reports.", inputSchema={"type":"object"}),
        Tool(name="audit_pkgbuild", description="Audit PKGBUILD for security.", inputSchema={"type":"object", "properties":{"content":{"type":"string"}}, "required":["content"]}),
        Tool(name="get_aur_comments", description="Fetch comments for a package.", inputSchema={"type":"object", "properties":{"package_name":{"type":"string"}}, "required":["package_name"]}),
        Tool(name="get_aur_comment_portal", description="Get manual comment link.", inputSchema={"type":"object", "properties":{"package_name":{"type":"string"}}, "required":["package_name"]}),
        Tool(name="post_comment_to_aur", description="Post comment to AUR. REQUIRES CREDENTIALS.", inputSchema={"type":"object", "properties":{"package_name":{"type":"string"}, "comment":{"type":"string"}}, "required":["package_name", "comment"]})
    ]

@server.call_tool()
async def call_tool(name, args):
    try:
        # 延迟加载，防止启动时污染
        import arch_ops_server.omega_aur as omega
        
        if name == "get_aur_news":
            res = await omega.get_aur_news()
            return [TextContent(type="text", text=json.dumps(res, indent=2))]
        elif name == "audit_pkgbuild":
            res = await omega.analyze_pkgbuild_security(args["content"])
            return [TextContent(type="text", text=json.dumps(res, indent=2))]
        elif name == "get_aur_comments":
            res = await omega.get_aur_comments(args["package_name"])
            return [TextContent(type="text", text=json.dumps(res, indent=2))]
        elif name == "get_aur_comment_portal":
            link = omega.generate_aur_comment_link(args["package_name"])
            return [TextContent(type="text", text=f"Portal: {link}")]
        elif name == "post_comment_to_aur":
            u, p = os.getenv("AUR_USER"), os.getenv("AUR_PASSWORD")
            if not u or not p: return [TextContent(type="text", text="Error: Credentials missing.")]
            res = await omega.post_aur_comment(args["package_name"], args["comment"], u, p)
            return [TextContent(type="text", text=json.dumps(res, indent=2))]
            
    except Exception as e:
        import traceback
        return [TextContent(type="text", text=f"OMEGA_ERROR: {str(e)}\n{traceback.format_exc()}")]
    
    return [TextContent(type="text", text="Unknown Tool")]

if __name__ == "__main__":
    async def run():
        async with stdio_server() as (read, write):
            await server.run(read, write, server.create_initialization_options())
    asyncio.run(run())
