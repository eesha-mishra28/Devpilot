from mcp.server.fastmcp import FastMCP

from mcp_tools.tools import (
    list_files,
    search_repository,
    read_file,
)


mcp = FastMCP("DevPilot")


@mcp.tool()
def list_repository_files() -> list[str]:
    """List all supported source files in the DevPilot repository."""
    return list_files()


@mcp.tool()
def search_codebase(query: str) -> list[dict]:
    """Search the DevPilot repository for a text query."""
    return search_repository(query)


@mcp.tool()
def read_repository_file(file_path: str) -> dict:
    """Read the contents of a specific source file."""
    return read_file(file_path)


if __name__ == "__main__":
    mcp.run()