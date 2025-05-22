from typing import Any
import httpx
import urllib.parse
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("riot")

# Constants
RIOT_API_BASE = "https://asia.api.riotgames.com"
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
ACCOUNT_ENDPOINT = "/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}"
REGION = "sg1"

# Helper function to make requests to the Riot API
async def make_riot_request(url: str) -> dict[str, Any] | None:
    """Make a request to the Riot API with proper error handling."""
    headers = {
        "X-Riot-Token": RIOT_API_KEY
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

# MCP tool to get a Riot account by game name and tag line
@mcp.tool()
async def get_account(game_name: str, tag_line: str) -> dict[str, Any] | None:
    """Get a Riot account by game name and tag line.
    
    Args:
        game_name: The in-game name of the player
        tag_line: The player's tag line (without the '#')
        
    Returns:
        dict: Player account data if found, None otherwise
        
    Raises:
        ValueError: If input parameters are invalid
        Exception: For other unexpected errors
    """
    if not game_name or not isinstance(game_name, str):
        raise ValueError("Game name must be a non-empty string")
    if not tag_line or not isinstance(tag_line, str):
        raise ValueError("Tag line must be a non-empty string")
    
    try:
        # Format the URL with proper URL encoding
        encoded_game_name = urllib.parse.quote(game_name)
        encoded_tag_line = urllib.parse.quote(tag_line)
        url = f"{RIOT_API_BASE}{ACCOUNT_ENDPOINT}".format(
            gameName=encoded_game_name,
            tagLine=encoded_tag_line
        )
        
        response = await make_riot_request(url)
        
        if response is None:
            # Log the failed attempt (you might want to add proper logging here)
            print(f"Failed to retrieve account for {game_name}#{tag_line}")
            
        return response
        
    except Exception as e:
        # Log the error and re-raise with a more descriptive message
        error_msg = f"Error fetching account data for {game_name}#{tag_line}: {str(e)}"
        print(error_msg)
        raise Exception(error_msg) from e

async def main():
    # Example usage of get_account
    result = await get_account("ball ji song", "2004")
    print("Account data:", result)

if __name__ == "__main__":
    print("Starting MCP server...")
    # Run the async main function
    import asyncio
    asyncio.run(main())
    # Start the MCP server
    mcp.run(transport='stdio')