"""MCP server for read-only ad matching."""

import json

from mcp.server.fastmcp import FastMCP

from .qdrant_service import match_ads


# Initialize FastMCP server
mcp = FastMCP("ad-injector")


@mcp.tool()
def ads_match(query: str, top_k: int = 10) -> str:
    """Match ads by text query. Returns similar ads based on semantic similarity.
    
    Args:
        query: Text query to match against ads
        top_k: Number of results to return (default: 10, max: 100)
        
    Returns:
        JSON string containing list of matching ads with scores and metadata
    """
    if not query or not isinstance(query, str):
        raise ValueError("query parameter is required and must be a string")
    
    if not isinstance(top_k, int) or top_k < 1 or top_k > 100:
        raise ValueError("top_k must be an integer between 1 and 100")
    
    # Call the safe match_ads wrapper
    results = match_ads(text=query, top_k=top_k)
    
    # Return results as JSON string
    return json.dumps(results, indent=2)


def run_server():
    """Run the MCP server using stdio transport."""
    mcp.run(transport="stdio")
