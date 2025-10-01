# src/homeharvest_mcp/server.py
# An MCP server exposing a single tool `scrape_properties` that calls HomeHarvest.
# Uses FastMCP from the official MCP Python SDK.

from __future__ import annotations
from typing import Optional, List, Dict, Any
import json

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("homeharvest-mcp")


@mcp.tool()
def ping() -> str:
    """Health check for the server. Returns 'ok' if the server is running."""
    return "ok"


@mcp.tool()
def scrape_properties(
    location: str,
    listing_type: str = "for_sale",  # one of: for_sale, for_rent, sold, pending
    past_days: Optional[int] = None,
    date_from: Optional[str] = None,  # "YYYY-MM-DD"
    date_to: Optional[str] = None,    # "YYYY-MM-DD"
    radius: Optional[float] = None,   # miles; only applies if location is a specific address
    foreclosure: bool = False,
    mls_only: bool = False,
    limit: Optional[int] = None,      # truncate results if provided
) -> List[Dict[str, Any]]:
    """
    Fetch property data from Realtor.com via HomeHarvest and return JSON rows.

    Args:
        location: e.g. "San Diego, CA" or "123 Main St, San Diego, CA 92104"
        listing_type: "for_sale" | "for_rent" | "sold" | "pending"
        past_days: filter by last N days (sold date if listing_type='sold', list date otherwise)
        date_from, date_to: alternative to past_days ("YYYY-MM-DD")
        radius: miles around an address (only if 'location' is a specific address)
        foreclosure: include foreclosures
        mls_only: only MLS listings
        limit: max records to return (server-side truncation)

    Returns:
        A list[dict] JSON-serializable table of properties (MLS-like fields).
    """
    try:
        # HomeHarvest is included in your repo (package name: homeharvest)
        # No network key required; it scrapes Realtor.com.
        from homeharvest import scrape_property  # type: ignore
    except Exception as e:
        # Make the error visible to the client
        return [{"error": "homeharvest import failed", "details": str(e)}]

    try:
        rows = scrape_property(
            location=location,
            listing_type=listing_type,
            past_days=past_days,
            date_from=date_from,
            date_to=date_to,
            radius=radius,
            foreclosure=foreclosure,
            mls_only=mls_only,
            return_type="raw",   # ensures JSON-friendly list[dict]
        )
        if limit is not None and isinstance(rows, list):
            rows = rows[: int(limit)]
        return rows
    except Exception as e:
        return [{"error": "scrape failed", "details": str(e)}]


def main() -> None:
    # Start the MCP server using STDIO transport (what Smithery expects unless overridden)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
