from mcp.types import Tool
from .omega_aur import analyze_pkgbuild_security, get_aur_comments, get_arch_news_portal, generate_aur_comment_link
import json

OMEGA_TOOLS = [
    Tool(
        name="audit_pkgbuild",
        description="Audit a PKGBUILD file for potential security risks.",
        inputSchema={ "type": "object", "properties": { "content": {"type": "string"} }, "required": ["content"] }
    ),
    Tool(
        name="get_aur_comments",
        description="Fetch community comments for an AUR package.",
        inputSchema={ "type": "object", "properties": { "package_name": {"type": "string"} }, "required": ["package_name"] }
    ),
    Tool(
        name="get_arch_news_portal",
        description="Get a direct link to the latest official Arch Linux news and announcements.",
        inputSchema={ "type": "object", "properties": {} }
    ),
    Tool(
        name="get_aur_comment_portal",
        description="Generate a direct link to the AUR package comment section.",
        inputSchema={ "type": "object", "properties": { "package_name": {"type": "string"} }, "required": ["package_name"] }
    )
]
