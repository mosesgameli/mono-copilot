"""
Whitelist of authorized sources by country and type.
Used for source verification in BA/PE agents.
"""

from typing import Dict, List


# Authorized sources by country and type
AUTHORIZED_SOURCES: Dict[str, Dict[str, List[str]]] = {
    "Nigeria": {
        "government": [
            "ncc.gov.ng",
            "firs.gov.ng",
            "naicom.gov.ng",
            "cbn.gov.ng",
            "naira.gov.ng",
        ],
        "industry": [
            "gsma.com",
            "statista.com",
            "idcafrica.com",
        ],
        "academic": [
            "unilag.edu.ng",
            "ui.edu.ng",
        ],
    },
    "Ghana": {
        "government": [
            "nca.org.gh",
            "mofep.gov.gh",
            "bog.org.gh",
        ],
        "industry": [
            "gsma.com",
            "statista.com",
        ],
        "academic": [],
    },
    "Kenya": {
        "government": [
            "cma.or.ke",
            "ica.go.ke",
            "cbr.go.ke",
        ],
        "industry": [
            "gsma.com",
            "statista.com",
        ],
        "academic": [],
    },
    "South Africa": {
        "government": [
            "icasa.org.za",
            "sars.gov.za",
            "treasury.gov.za",
        ],
        "industry": [
            "gsma.com",
            "statista.com",
        ],
        "academic": [],
    },
    "Egypt": {
        "government": [
            "ntra.gov.eg",
            "egbank.org.eg",
        ],
        "industry": [
            "gsma.com",
            "statista.com",
        ],
        "academic": [],
    },
    "Global": {
        "industry": [
            "gsma.com",
            "statista.com",
            "gartner.com",
            "forrester.com",
            "idcafrica.com",
        ],
        "academic": [
            "ieee.org",
            "acm.org",
            "scholar.google.com",
        ],
    },
}


def is_source_authorized(source_url: str) -> bool:
    """
    Check if a source URL is in the authorized sources whitelist.
    
    Args:
        source_url: URL to verify
    
    Returns:
        True if authorized, False otherwise
    """
    # TODO: Implement whitelist checking logic
    pass


def get_authority_level(source_url: str) -> str:
    """
    Get authority level for a source (high, medium, low).
    
    Args:
        source_url: URL to check
    
    Returns:
        Authority level: "high", "medium", or "low"
    """
    # TODO: Implement authority level detection
    pass
