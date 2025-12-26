from mcp.types import Tool, TextContent
from .omega_aur import analyze_pkgbuild_security, get_aur_comments, post_aur_comment
import json

OMEGA_TOOLS = [
    Tool(
        name="audit_pkgbuild",
        description="Audit a PKGBUILD file for potential security risks.",
        inputSchema={
            "type": "object",
            "properties": {
                "content": {"type": "string"}
            },
            "required": ["content"]
        }
    ),
    Tool(
        name="get_aur_comments",
        description="Fetch community comments for an AUR package.",
        inputSchema={
            "type": "object",
            "properties": {
                "package_name": {"type": "string"}
            },
            "required": ["package_name"]
        }
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
