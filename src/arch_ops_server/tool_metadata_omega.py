from mcp.types import Tool

OMEGA_TOOLS = [
    Tool(
        name="audit_pkgbuild",
        description="Audit a PKGBUILD file for potential security risks and malicious patterns.",
        inputSchema={
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Full content of the PKGBUILD file"}
            },
            "required": ["content"]
        }
    ),
    Tool(
        name="get_aur_comments",
        description="Fetch the latest community comments for a specific AUR package.",
        inputSchema={
            "type": "object",
            "properties": {
                "package_name": {"type": "string", "description": "Name of the AUR package"}
            },
            "required": ["package_name"]
        }
    )
]
