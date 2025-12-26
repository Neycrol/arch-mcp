from mcp.types import Tool
from .omega_aur import analyze_pkgbuild_security, get_aur_comments, get_aur_news, submit_aur_request
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
        description="Fetch the latest news and announcements from Arch Linux main site.",
        inputSchema={ "type": "object", "properties": {} }
    ),
    Tool(
        name="submit_aur_package_request",
        description="Submit a formal request (orphan/deletion/merge) for an AUR package. REQUIRES CREDENTIALS.",
        inputSchema={
            "type": "object",
            "properties": {
                "package_name": {"type": "string"},
                "request_type": {"type": "string", "enum": ["orphan", "deletion", "merge"]},
                "comments": {"type": "string", "description": "Reason for the request"}
            },
            "required": ["package_name", "request_type", "comments"]
        }
    )
]
