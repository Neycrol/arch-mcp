import sys
import os
import json
import asyncio
from pathlib import Path
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

# 1. 物理自感知
src_dir = str(Path(__file__).resolve().parent.parent)
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# 2. 构造奥米加影子服务器 (不再导入原版 server，直接自建以确保启动稳健)
server = Server("aur-omega")

@server.list_tools()
async def list_tools():
    # 静态返回工具列表，不依赖任何外部导入
    return [
        Tool(name="get_aur_news", description="Fetch Arch Linux News", inputSchema={"type":"object"}),
        Tool(name="audit_pkgbuild", description="Audit PKGBUILD", inputSchema={"type":"object", "properties":{"content":{"type":"string"}}})
    ]

@server.call_tool()
async def call_tool(name, args):
    # 仅在调用时进行“延迟加载”
    try:
        from arch_ops_server.omega_aur import get_aur_news, analyze_pkgbuild_security
        if name == "get_aur_news":
            res = await get_aur_news()
            return [TextContent(type="text", text=json.dumps(res, indent=2))]
        elif name == "audit_pkgbuild":
            res = await analyze_pkgbuild_security(args["content"])
            return [TextContent(type="text", text=json.dumps(res, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=f"LAZY_LOAD_ERROR: {str(e)}")]
    return [TextContent(type="text", text="Tool not found")]

async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        with open("/tmp/omega_critical.log", "w") as f:
            f.write(str(e))
