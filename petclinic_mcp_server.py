import json
import os
from mcp.server.fastmcp import FastMCP
import httpx

# Get port from environment variable (for Cloud Foundry) or default to 8001
port = int(os.environ.get('PORT', 8001))

# Initialize FastMCP server
mcp = FastMCP("petclin_mcp_server", port=port)

HEADERS = {
    "Accept": "application/json"
}

def get_secure_client():
    return httpx.AsyncClient(
        verify=False,               # SSL certificate validation enabled
        timeout=10.0,
        headers=HEADERS
    )


@mcp.tool()
async def fetch_petsByStatus(status: str) -> dict:
    """Retrieve pets from petstore api"""
    # Use 'async def' for operations involving network calls, file I/O, etc.
    # This prevents blocking the server while waiting for external operations.
    url = f"https://petstore3.swagger.io/api/v3/pet/findByStatus?status={status}"
    async with get_secure_client() as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()
@mcp.prompt()
def generate_petstore_analysis_prompt(status: str = "available") -> str:
    return f"""
        Your task is to analyze the current state of the pet inventory system using the `fetch_petsByStatus` tool. You will be querying pets by their status — in this case, status = '{status}'.

        The available status values are:
        - available
        - pending
        - sold

        Task Instructions:

        1. Fetch Data
        - Use: `fetch_petsByStatus(status='{status}')` to retrieve the current list of pets with this status.

        2. Parse and Analyze
        For each pet in the result:
        - Extract and organize the following information:
            - Pet ID
            - Name
            - Category (if present)
            - Tags (if any)
            - Photo URLs
        - Group pets by **category** and **tag**.
        - Count how many pets are in each category.
        - Identify any pets with missing names, categories, or tags and report them as data quality issues.

        3. Synthesize Insights
        - Summarize trends in the available pets:
            - What are the most common categories or tags?
            - Are there any duplicate names or unusual patterns?
        - Suggest operational actions based on the data, such as:
            - Which categories need more supply?
            - Are there overly tagged or under-tagged pets?
            - Are certain names used too often, reducing distinctiveness?

        4. Output Format
        Present your findings in the following structure:
        - **Section 1: Pet Summary Table**
            - A table of all pets with the selected status
        - **Section 2: Grouped Analysis**
            - Pet counts by category and by tag
        - **Section 3: Data Quality Issues**
            - List of pets missing key fields
        - **Section 4: Operational Recommendations**
            - Insightful next steps to improve inventory, naming, and tagging

        5. Optional Enhancement
        - If photo URLs are present, identify which pets are missing photo URLs and quantify this.
        - Suggest ways to enrich metadata or improve tagging consistency.

        Goal:
        Provide a detailed inventory health report based on pets with status = '{status}', uncover insights, and recommend actions for business or operational improvement.
        """



if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='sse')

