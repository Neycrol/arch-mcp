from mcp.types import Tool
from .omega_aur import analyze_pkgbuild_security, get_aur_comments, get_aur_news, post_aur_comment, edit_aur_comment
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
        name="post_comment_to_aur",
        description="Post a comment to an AUR package page. REQUIRES CREDENTIALS.",
        inputSchema={
            "type": "object",
            "properties": { "package_name": {"type": "string"}, "comment": {"type": "string"} },
            "required": ["package_name", "comment"]
        }
    ),
    Tool(
        name="edit_aur_comment",
        description="Edit an existing comment on an AUR package page. REQUIRES CREDENTIALS.",
        inputSchema={
            "type": "object",
            "properties": { 
                "package_name": {"type": "string"}, 
                "comment_id": {"type": "string"}, 
                "new_comment": {"type": "string"} 
            },
            "required": ["package_name", "comment_id", "new_comment"]
        }
    )
]
