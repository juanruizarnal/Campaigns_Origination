"""Helper functions for Streamlit frontend.

Provides formatting, validation, and utility functions.
"""

from datetime import datetime
from typing import Optional


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format a number as percentage string."""
    return f"{value:.{decimals}f}%"


def format_currency(value, currency: str = "EUR") -> str:
    """Format a number as currency string.
    
    Safely handles non-numeric values from Airtable (strings, lists, None).
    """
    symbols = {"EUR": "€", "USD": "$", "GBP": "£"}
    symbol = symbols.get(currency, currency)
    
    # Handle None
    if value is None:
        return "N/A"
    
    # Handle lists (Airtable sometimes returns lists)
    if isinstance(value, list):
        value = value[0] if value else None
        if value is None:
            return "N/A"
    
    # Try to convert to float
    try:
        value = float(value)
    except (ValueError, TypeError):
        return "N/A"
    
    if value >= 1_000_000_000:
        return f"{symbol}{value / 1_000_000_000:.1f}B"
    elif value >= 1_000_000:
        return f"{symbol}{value / 1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{symbol}{value / 1_000:.1f}K"
    else:
        return f"{symbol}{value:.0f}"


def format_date(date_str: str, output_format: str = "%d/%m/%Y") -> str:
    """Format date string to display format."""
    if not date_str:
        return "N/A"
    
    try:
        # Try common input formats
        for fmt in ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%S"]:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime(output_format)
            except ValueError:
                continue
        return date_str
    except Exception:
        return date_str


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to max length with suffix."""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def get_fei_status_emoji(status: str) -> str:
    """Get emoji for FEI status."""
    emoji_map = {
        "Eligible": "✅",
        "Not_Eligible": "❌",
        "Partial": "⚠️",
        "Unknown": "❓",
    }
    return emoji_map.get(status, "❓")


def get_campaign_status_emoji(status: str) -> str:
    """Get emoji for campaign status."""
    emoji_map = {
        "Draft": "📝",
        "Pending_Approval": "⏳",
        "Approved": "✅",
        "Active": "🚀",
        "Completed": "✔️",
        "Cancelled": "❌",
    }
    return emoji_map.get(status, "📋")


def get_urgency_emoji(urgency: str) -> str:
    """Get emoji for urgency level."""
    emoji_map = {
        "High": "🔴",
        "Medium": "🟡",
        "Low": "🟢",
    }
    return emoji_map.get(urgency, "⚪")


def validate_email(email: str) -> bool:
    """Basic email validation."""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """Basic URL validation."""
    import re
    pattern = r'^https?:\/\/[a-zA-Z0-9][-a-zA-Z0-9@:%._\+~#=]{0,255}\.[a-z]{2,6}(\/[-a-zA-Z0-9@:%_\+.~#?&\/=]*)?$'
    return bool(re.match(pattern, url, re.IGNORECASE))


def parse_keywords(keywords_str: str) -> list:
    """Parse comma-separated keywords string to list."""
    if not keywords_str:
        return []
    return [k.strip() for k in keywords_str.split(",") if k.strip()]


def get_sector_options() -> list:
    """Get list of available sectors."""
    return [
        "Aerospace",
        "Agriculture",
        "Automotive",
        "Chemicals",
        "Construction",
        "Defense",
        "Energy",
        "Food & Beverage",
        "Healthcare",
        "Manufacturing",
        "Renewable Energy",
        "Retail",
        "Services",
        "Technology",
        "Telecommunications",
        "Transportation",
    ]


def get_company_sector_options() -> list:
    """Get list of sector options for Empresas page."""
    return [
        "Renewable Energy",
        "Real Estate",
        "Defense & Aerospace",
    ]


def get_company_activity_options(sectors: Optional[list[str]] = None) -> list:
    """Get activity options associated to selected sectors."""
    if not sectors:
        return []

    activity_map = {
        "Real Estate": [
            "Mixed-Use Developments",
            "Residential Development",
            "Retail & Shopping Centers",
            "Senior Living",
            "Student Housing",
        ],
        "Renewable Energy": [
            "Battery Storage (BESS)",
            "Biogas",
            "Biomass",
            "Geothermal",
            "Green Hydrogen Production",
            "Hydropower",
            "Ocean Energy",
            "Autoconsumption",
        ],
        "Defense & Aerospace": [
            "Defense & Aerospace",
        ],
    }

    activities: list[str] = []
    for sector in sectors:
        for activity in activity_map.get(sector, []):
            if activity not in activities:
                activities.append(activity)
    return activities


def get_country_options() -> list:
    """Get list of available countries."""
    return [
        ("ES", "España 🇪🇸"),
        ("FR", "Francia 🇫🇷"),
        ("DE", "Alemania 🇩🇪"),
        ("IT", "Italia 🇮🇹"),
        ("PT", "Portugal 🇵🇹"),
        ("NL", "Países Bajos 🇳🇱"),
        ("BE", "Bélgica 🇧🇪"),
        ("PL", "Polonia 🇵🇱"),
        ("AT", "Austria 🇦🇹"),
        ("IE", "Irlanda 🇮🇪"),
    ]


def get_fei_status_options() -> list:
    """Get list of FEI status options."""
    return [
        ("", "Todos"),
        ("Eligible", "✅ Eligible"),
        ("Not_Eligible", "❌ Not Eligible"),
        ("Partial", "⚠️ Partial"),
        ("Unknown", "❓ Unknown"),
    ]
