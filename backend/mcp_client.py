import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def create_server_parameters(project_path: str):

    return StdioServerParameters(
        command="python",
        args=[
            "-m",
            "mcp_tools.server",
        ],
        env={
            "DEVPILOT_PROJECT_PATH": project_path,
        },
    )


async def get_mcp_tools_async(
    project_path: str,
):

    server_params = create_server_parameters(
        project_path
    )

    async with stdio_client(
        server_params
    ) as (read, write):

        async with ClientSession(
            read,
            write
        ) as session:

            await session.initialize()

            tools = await session.list_tools()

            return tools.tools


async def call_mcp_tool_async(
    project_path: str,
    tool_name: str,
    arguments: dict,
):

    server_params = create_server_parameters(
        project_path
    )

    async with stdio_client(
        server_params
    ) as (read, write):

        async with ClientSession(
            read,
            write
        ) as session:

            await session.initialize()

            result = await session.call_tool(
                tool_name,
                arguments,
            )

            return result


def get_mcp_tools(
    project_path: str,
):

    return asyncio.run(
        get_mcp_tools_async(
            project_path
        )
    )


def call_mcp_tool(
    project_path: str,
    tool_name: str,
    arguments: dict,
):

    return asyncio.run(
        call_mcp_tool_async(
            project_path,
            tool_name,
            arguments,
        )
    )