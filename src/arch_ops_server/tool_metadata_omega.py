from mcp.types import Tool
from .omega_aur import analyze_pkgbuild_security, get_aur_comments, get_aur_news, generate_aur_comment_link
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
        name="get_aur_news",
        description="Fetch the latest news and announcements from Arch Linux main site.",
        inputSchema={ "type": "object", "properties": {} }
    ),
    Tool(
        name="get_aur_comment_portal",
        description="Generate a direct link to the AUR package comment section for manual posting.",
        inputSchema={
            "type": "object",
            "properties": { "package_name": {"type": "string"} },
            "required": ["package_name"]
        }
    )
]
