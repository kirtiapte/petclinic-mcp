import json
import os
from mcp.server.fastmcp import FastMCP
import httpx

# Get port from environment variable (for Cloud Foundry) or default to 8001
port = int(os.environ.get('PORT', 8001))

# Initialize FastMCP server
mcp = FastMCP("research", port=port)

@mcp.tool()
async def fetch_petsByStatus(status: str) -> dict:
    """Retrieve pets from petstore api"""
    # Use 'async def' for operations involving network calls, file I/O, etc.
    # This prevents blocking the server while waiting for external operations.
    url = f"https://petstore3.swagger.io/api/v3/pet/findByStatus?status={status}"
    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()



if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='sse')