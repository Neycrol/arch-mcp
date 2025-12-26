import sys
import os
import json
import asyncio
from pathlib import Path
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

# 1. 物理自感知：锁定核心路径
current_file = Path(__file__).resolve()
src_dir = str(current_file.parent.parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# 2. 初始化奥米加影子服务器
server = Server("aur-omega")

@server.list_tools()
async def list_tools():
    """【全武装列表】物理补完所有 5 把奥米加利斧"""
    return [
        Tool(name="get_aur_news", description="Fetch full Arch Linux news reports from archlinux.org.", inputSchema={"type":"object"}),
        Tool(name="audit_pkgbuild", description="Audit a PKGBUILD content for security risks.", inputSchema={"type":"object", "properties":{"content":{"type":"string"}}, "required":["content"]}),
        Tool(name="get_aur_comments", description="Fetch comments for an AUR package.", inputSchema={"type":"object", "properties":{"package_name":{"type":"string"}}, "required":["package_name"]}),
        Tool(name="get_aur_comment_portal", description="Get manual comment link.", inputSchema={"type":"object", "properties":{"package_name":{"type":"string"}}, "required":["package_name"]}),
        Tool(name="post_comment_to_aur", description="[EXPERIMENTAL] Post comment to AUR. REQUIRES CREDENTIALS.", inputSchema={"type":"object", "properties":{"package_name":{"type":"string"}, "comment":{"type":"string"}}, "required":["package_name", "comment"]})
    ]

@server.call_tool()
async def call_tool(name, args):
    """【逻辑路由】延迟加载并精准分发"""
    try:
        # 物理导入校准
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
            if not u or not p: return [TextContent(type="text", text="Credentials missing")]
            res = await omega.post_aur_comment(args["package_name"], args["comment"], u, p)
            return [TextContent(type="text", text=json.dumps(res, indent=2))]
            
    except Exception as e:
        import traceback
        return [TextContent(type="text", text=f"OMEGA_ENGINE_ERROR: {str(e)}\n{traceback.format_exc()}")]
    
    return [TextContent(type="text", text="Unknown Tool")]

if __name__ == "__main__":
    async def run():
        async with stdio_server() as (read, write):
            await server.run(read, write, server.create_initialization_options())
    asyncio.run(run())
