import sys
import os
import json
import asyncio
import logging
from pathlib import Path

# --- [终极物理禁言：开启无缓冲模式，彻底终结 Stdio 死锁] ---
# 强制使用 stderr 进行所有非协议输出
logging.basicConfig(level=logging.WARNING, stream=sys.stderr)

# 关键：物理重定义 stdout 为无缓冲模式，确保数据实时流出，不产生堆积
sys.stdout.reconfigure(line_buffering=True)

# 1. 物理自感知
src_dir = str(Path(__file__).resolve().parent.parent)
if src_dir not in sys.path: sys.path.insert(0, src_dir)

from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

server = Server("aur-omega")

@server.list_tools()
async def list_tools():
    return [
        Tool(name="get_aur_news", description="Fetch short Arch news summaries.", inputSchema={"type":"object"}),
        Tool(name="audit_pkgbuild", description="Audit security.", inputSchema={"type":"object", "properties":{"content":{"type":"string"}}})
    ]

@server.call_tool()
async def call_tool(name, args):
    try:
        import arch_ops_server.omega_aur as omega
        if name == "get_aur_news":
            # 物理限制：每篇新闻截取前 500 字符，彻底解决管道拥塞
            res = await omega.get_aur_news()
            for r in res:
                if "report" in r: r["report"] = r["report"][:500] + "... [Trimmied]"
            return [TextContent(type="text", text=json.dumps(res, indent=2))]
        elif name == "audit_pkgbuild":
            res = await omega.analyze_pkgbuild_security(args["content"])
            return [TextContent(type="text", text=json.dumps(res, indent=2))]
    except Exception as e:
        return [TextContent(type="text", text=f"ERROR: {str(e)}")]
    return [TextContent(type="text", text="Unknown Tool")]

if __name__ == "__main__":
    async def run():
        async with stdio_server() as (read, write):
            await server.run(read, write, server.create_initialization_options())
    asyncio.run(run())
