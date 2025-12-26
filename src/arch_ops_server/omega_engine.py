from .server import server as base_server
from .tool_metadata_omega import OMEGA_TOOLS
from .omega_aur import analyze_pkgbuild_security, get_aur_comments, get_aur_news, generate_aur_comment_link
from mcp.types import TextContent
import json

original_list_tools = base_server.list_tools()
@base_server.list_tools()
async def list_tools_omega():
    tools = await original_list_tools()
    return tools + OMEGA_TOOLS

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

server = base_server
