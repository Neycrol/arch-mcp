import sys
import os
from pathlib import Path

# --- [物理自感知：解决 PYTHONPATH 丢失之痛] ---
current_file = Path(__file__).resolve()
# 我们的目录结构是 REPO/src/arch_ops_server/omega_engine.py
# 我们需要将 REPO/src 加入 sys.path
src_dir = str(current_file.parent.parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from .server import server as base_server
from .tool_metadata_omega import OMEGA_TOOLS
from .omega_aur import analyze_pkgbuild_security, get_aur_comments, get_aur_news, generate_aur_comment_link
from mcp.types import TextContent
import json

# 劫持工具列表
original_list_tools = base_server.list_tools()
@base_server.list_tools()
async def list_tools_omega():
    tools = await original_list_tools()
    return tools + OMEGA_TOOLS

# 劫持工具调用
original_call_tool = base_server.call_tool()
@base_server.call_tool()
async def call_tool_omega(name, arguments):
    if name == "audit_pkgbuild":
        result = await analyze_pkgbuild_security(arguments["content"])
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    elif name == "get_aur_comments":
        result = await get_aur_comments(arguments["package_name"])
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    elif name == "get_aur_news":
        result = await get_aur_news()
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    elif name == "get_aur_comment_portal":
        link = generate_aur_comment_link(arguments["package_name"])
        return [TextContent(type="text", text=f"Portal Ready: {link}\n\nPlease click the link to post your comment manually.")]
    
    return await original_call_tool(name, arguments)

if __name__ == "__main__":
    from mcp.server.stdio import stdio_server
    import asyncio
    async def run():
        async with stdio_server() as (read, write):
            await base_server.run(read, write, base_server.create_initialization_options())
    asyncio.run(run())
