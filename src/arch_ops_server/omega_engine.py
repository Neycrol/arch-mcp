import sys
import os
from pathlib import Path

# --- [物理自感知：解决导入之痛] ---
current_file = Path(__file__).resolve()
# 锁定 REPO/src 目录
src_dir = str(current_file.parent.parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# 核心修正：使用绝对导入，彻底规避 "no known parent package" 报错
import arch_ops_server.server as server_mod
from arch_ops_server.tool_metadata_omega import OMEGA_TOOLS
from arch_ops_server.omega_aur import analyze_pkgbuild_security, get_aur_comments, get_aur_news, generate_aur_comment_link
from mcp.types import TextContent
import json

base_server = server_mod.server

# 劫持工具列表
original_list_tools = base_server.list_tools()
@base_server.list_tools()
async def list_tools_omega():
    tools = await original_list_tools()
    return tools + OMEGA_TOOLS

# 劫持工具调用
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
    
    # 既然我们重写了 call_tool，我们需要手动分发原有的工具
    # 注意：此处需谨慎，原版 server 可能已经定义了 call_tool 处理逻辑
    # 理想方案是保持原版 server 的装饰器不被覆盖
    # 为此，我们在这里只处理奥米加工具，其他交给原版
    return await server_mod.call_tool(name, arguments)

if __name__ == "__main__":
    from mcp.server.stdio import stdio_server
    import asyncio
    async def run():
        async with stdio_server() as (read, write):
            await base_server.run(read, write, base_server.create_initialization_options())
    asyncio.run(run())
