from .server import server as base_server
from .tool_metadata_omega import OMEGA_TOOLS
from .omega_aur import analyze_pkgbuild_security, get_aur_comments, get_aur_news, post_aur_comment
from mcp.types import TextContent
import json
import os

original_list_tools = base_server.list_tools()
@base_server.list_tools()
async def list_tools_omega():
    tools = await original_list_tools()
    return tools + OMEGA_TOOLS

@base_server.call_tool()
async def call_tool_omega(name, arguments):
    # 从环境变量读取 AURSID
    aursid = os.getenv("AUR_SID")

    if name == "audit_pkgbuild":
        result = await analyze_pkgbuild_security(arguments["content"])
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    elif name == "get_aur_comments":
        result = await get_aur_comments(arguments["package_name"])
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    elif name == "get_aur_news":
        result = await get_aur_news()
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    elif name == "post_comment_to_aur":
        if not aursid: return [TextContent(type="text", text="Error: AUR_SID not set in config.")]
        result = await post_aur_comment(arguments["package_name"], arguments["comment"], aursid)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    return await original_call_tool(name, arguments)

server = base_server
