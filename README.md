# Riot API MCP Server

A FastMCP server that provides access to Riot Games API endpoints, specifically for retrieving player account information.

## Features

- Retrieve Riot account information by game name and tag line
- Secure API key management using environment variables
- Built with Python and FastMCP for efficient API handling
- Proper error handling and input validation

## Prerequisites

- Python 3.8+
- Riot Games API Key (from [Riot Developer Portal](https://developer.riotgames.com/))
- Required Python packages (see [Installation](#installation))

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd riot-mcp-server
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
   If you don't have a requirements.txt, install the dependencies manually:
   ```bash
   pip install httpx python-dotenv
   ```

3. Create a `.env` file in the project root and add your Riot API key:
   ```
   RIOT_API_KEY=your_api_key_here
   ```

## Usage

1. Start the MCP server:
   ```bash
   python main.py
   ```

2. The server will start and be ready to accept requests.

### Available Endpoints

#### Get Account by Riot ID

- **Endpoint**: `get_account`
- **Description**: Retrieve account information using game name and tag line
- **Parameters**:
  - `game_name` (string): The player's in-game name
  - `tag_line` (string): The player's tag line (without the '#')

Example request:
```json
{
  "game_name": "PlayerName",
  "tag_line": "NA1"
}
```

## Error Handling

The API returns appropriate error responses for:
- Invalid input parameters
- Riot API errors
- Network issues
- Server errors

## Configuration

Configuration is handled through environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `RIOT_API_KEY` | Your Riot Games API key | - |
| `REGION` | Default region for API calls | `sg1` |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## Acknowledgments

- [Riot Games API](https://developer.riotgames.com/)
- [httpx](https://www.python-httpx.org/)
