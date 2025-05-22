# Standard library imports
import asyncio
import os
import urllib.parse
from typing import Any

# Third-party imports
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Local application imports
from exceptions import (
    RiotAPIError,
    RiotAPINotFoundError,
    RiotAPIRateLimitError,
    RiotAPIUnauthorizedError,
)

load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("riot")

# Constants
RIOT_API_BASE = "https://asia.api.riotgames.com"
RIOT_API_BASE_V2 = "https://sg2.api.riotgames.com"
RIOT_API_KEY = os.getenv("RIOT_API_KEY")
ACCOUNT_ENDPOINT = "/riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}"
LOL_ACCOUNT_PUUID_ENDPOINT = "/lol/summoner/v4/summoners/by-puuid/{encryptedPUUID}"

# Helper function to make requests to the Riot API
async def make_riot_request(url: str) -> dict[str, Any]:
    """Make a request to the Riot API with proper error handling.
    
    Args:
        url: The full URL to make the request to
        
    Returns:
        dict: The JSON response from the API
        
    Raises:
        RiotAPIRateLimitError: If rate limit is exceeded
        RiotAPIUnauthorizedError: If API key is invalid or missing
        RiotAPINotFoundError: If the requested resource is not found
        httpx.RequestError: If there's an issue with the request
        ValueError: If the response is not valid JSON
    """
    if not RIOT_API_KEY:
        raise ValueError("RIOT_API_KEY environment variable is not set")
        
    headers = {
        "X-Riot-Token": RIOT_API_KEY,
        "Accept": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, timeout=30.0)
            
            if response.status_code == 429:
                retry_after = response.headers.get('Retry-After', 'unknown')
                raise RiotAPIRateLimitError(
                    f"Rate limit exceeded. Retry after: {retry_after} seconds"
                )
            elif response.status_code == 401:
                raise RiotAPIUnauthorizedError("Invalid or missing API key")
            elif response.status_code == 404:
                raise RiotAPINotFoundError(f"Resource not found: {url}")
            elif response.status_code >= 500:
                raise RiotAPIError(f"Riot API server error: {response.status_code}")
                
            response.raise_for_status()
            return response.json()
            
    except httpx.RequestError as e:
        raise RiotAPIError(f"Request to Riot API failed: {str(e)}") from e
    except ValueError as e:
        raise ValueError(f"Invalid JSON response from Riot API: {str(e)}") from e

# MCP tool to get a Riot account by game name and tag line
@mcp.tool()
async def get_account(game_name: str, tag_line: str) -> dict[str, Any] | None:
    """Get a Riot account by game name and tag line.
    
    Args:
        game_name: The in-game name of the player
        tag_line: The player's tag line (without the '#')
        
    Returns:
        dict: Player account data if found, None if not found
        
    Raises:
        ValueError: If input parameters are invalid or missing required data
        RiotAPIError: For Riot API related errors
        httpx.RequestError: For network-related errors
    """
    if not game_name or not isinstance(game_name, str):
        raise ValueError("Game name must be a non-empty string")
    if not tag_line or not isinstance(tag_line, str):
        raise ValueError("Tag line must be a non-empty string")
    
    # Format the URL with proper URL encoding
    encoded_game_name = urllib.parse.quote(game_name)
    encoded_tag_line = urllib.parse.quote(tag_line)
    url = f"{RIOT_API_BASE}{ACCOUNT_ENDPOINT}".format(
        gameName=encoded_game_name,
        tagLine=encoded_tag_line
    )
    
    try:
        return await make_riot_request(url)
    except RiotAPINotFoundError:
        # Account not found is a normal case, return None
        return None
    except RiotAPIError as e:
        # Log the error (in a real app, use proper logging)
        print(f"Riot API error: {str(e)}")
        raise
    except Exception as e:
        # Catch any other unexpected errors
        error_msg = f"Unexpected error fetching account data for {game_name}#{tag_line}: {str(e)}"
        print(error_msg)
        raise RuntimeError(error_msg) from e

@mcp.tool()
async def get_account_by_name(game_name: str, tag_line: str) -> dict[str, Any] | None:
    """Get a Riot account by game name and tag line.
    
    This function first retrieves the account information using the Riot ID (game name and tag line),
    then fetches the associated League of Legends account details using the PUUID.
    
    Args:
        game_name: The in-game name of the player (case-insensitive)
        tag_line: The player's tag line (without the '#')
        
    Returns:
        dict: Player account data if found, None if not found
        
    Raises:
        ValueError: If input parameters are invalid or missing required data
        RiotAPIError: For Riot API related errors
        RuntimeError: For unexpected errors during the process
        httpx.RequestError: For network-related errors
    """
    try:
        # Get the account information first
        account = await get_account(game_name, tag_line)
        if not account:
            return None
            
        # Get the League of Legends account details using the PUUID
        lol_account = await get_lol_account_by_puuid(account['puuid'])
        if not lol_account:
            print(f"No League of Legends account found for PUUID: {account['puuid']}")
            return None
            
        # Combine the account information
        return {
            **account,
            'lol_account': lol_account
        }
        
    except RiotAPINotFoundError:
        # Account not found is a normal case, return None
        return None
    except Exception as e:
        # Catch any other unexpected errors
        error_msg = f"Unexpected error fetching LoL account data for PUUID : {str(e)}"
        print(error_msg)
        raise RuntimeError(error_msg) from e

# MCP tool to get a Riot account by PUUID
@mcp.tool()
async def get_lol_account_by_puuid(puuid: str) -> dict[str, Any] | None:
    """Get a LoL account by PUUID.
    
    Args:
        puuid: The player's PUUID
        
    Returns:
        dict: Player account data if found, None if not found
        
    Raises:
        ValueError: If PUUID is invalid or missing required data
        RiotAPIError: For Riot API related errors
        httpx.RequestError: For network-related errors
    """
    if not puuid or not isinstance(puuid, str):
        raise ValueError("PUUID must be a non-empty string")
    
    url = f"{RIOT_API_BASE_V2}{LOL_ACCOUNT_PUUID_ENDPOINT}".format(
        encryptedPUUID=puuid
    )
    
    try:
        return await make_riot_request(url)
    except RiotAPINotFoundError:
        # Account not found is a normal case, return None
        return None
    except RiotAPIError as e:
        # Log the error (in a real app, use proper logging)
        print(f"Riot API error for PUUID {puuid}: {str(e)}")
        raise
    except Exception as e:
        # Catch any other unexpected errors
        error_msg = f"Unexpected error fetching LoL account data for PUUID {puuid}: {str(e)}"
        print(error_msg)
        raise RuntimeError(error_msg) from e

async def main():
    # Example usage of get_account
    result = await get_lol_account_by_puuid("7QglWNobi8ePux7aS08HRuI3hiX1DFcp4W9SKpxjsXUNh4dN8_8pQrr3T9wF2nc_m07WpDui5cQoHA")
    print("Account data:", result)

if __name__ == "__main__":
    print("Starting MCP server...")
    asyncio.run(main())
    mcp.run(transport='stdio')