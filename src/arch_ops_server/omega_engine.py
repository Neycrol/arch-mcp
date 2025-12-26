import sys
import os
import json
import asyncio
from pathlib import Path
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

# 物理自感知
current_file = Path(__file__).resolve()
src_dir = str(current_file.parent.parent)
if src_dir not in sys.path: sys.path.insert(0, src_dir)

server = Server("aur-omega")

@server.list_tools()
async def list_tools():
    from .tool_metadata_omega import OMEGA_TOOLS
    return OMEGA_TOOLS

@server.call_tool()
async def call_tool(name, args):
    try:
        from .omega_aur import analyze_pkgbuild_security, get_aur_comments, get_arch_news_portal, generate_aur_comment_link
        if name == "audit_pkgbuild":
            res = await analyze_pkgbuild_security(args["content"])
            return [TextContent(type="text", text=json.dumps(res, indent=2))]
        elif name == "get_aur_comments":
            res = await get_aur_comments(args["package_name"])
            return [TextContent(type="text", text=json.dumps(res, indent=2))]
        elif name == "get_arch_news_portal":
            res = get_arch_news_portal()
            return [TextContent(type="text", text=res)]
        elif name == "get_aur_comment_portal":
            res = generate_aur_comment_link(args["package_name"])
            return [TextContent(type="text", text=f"Portal: {res}")]
    except Exception as e:
        return [TextContent(type="text", text=f"ERROR: {str(e)}")]
    return [TextContent(type="text", text="Unknown Tool")]

if __name__ == "__main__":
    async def main():
        async with stdio_server() as (read, write):
            await server.run(read, write, server.create_initialization_options())
    asyncio.run(main())
