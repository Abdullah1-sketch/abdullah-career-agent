MANUAL_OPPORTUNITIES = []


def get_manual_opportunities() -> list[dict]:
    """
    Manual opportunities are disabled for now.

    This prevents fake/sample opportunities such as:
    - Manual sample
    - Example Saudi Company
    - example.com

    Real opportunities should come from trusted sources only.
    """
    return MANUAL_OPPORTUNITIES
