"""Main entry point for the ad-injector application."""

from .mcp_server import run_server


def main():
    """Main function for the ad-injector MCP server."""
    run_server()


if __name__ == "__main__":
    main()
