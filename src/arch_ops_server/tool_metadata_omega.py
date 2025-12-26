from mcp.types import Tool
from .omega_aur import analyze_pkgbuild_security, get_aur_comments, post_aur_comment, get_aur_news
import json

OMEGA_TOOLS = [
    Tool(
        name="audit_pkgbuild",
        description="Audit a PKGBUILD file for potential security risks.",
        inputSchema={
            "type": "object",
            "properties": { "content": {"type": "string"} },
            "required": ["content"]
        }
    ),
    Tool(
        name="get_aur_comments",
        description="Fetch community comments for an AUR package.",
        inputSchema={
            "type": "object",
            "properties": { "package_name": {"type": "string"} },
            "required": ["package_name"]
        }
    ),
    Tool(
        name="get_aur_news",
        description="Fetch the latest news and announcements from AUR homepage.",
        inputSchema={ "type": "object", "properties": {} }
    ),
    Tool(
        name="post_comment_to_aur",
        description="Post a comment to an AUR package page (Requires AUR credentials).",
        inputSchema={
            "type": "object",
            "properties": {
                "package_name": {"type": "string"},
                "comment": {"type": "string"}
            },
            "required": ["package_name", "comment"]
        }
    )
]
