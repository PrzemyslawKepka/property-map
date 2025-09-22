import re


def extract_coordinates(url: str) -> tuple[float, float] | None:
    """Extract latitude and longitude from a Google Maps URL.

    This function supports the two most common coordinate encodings used by
    Google Maps URLs:

    - The ``!3d<lat>!4d<lon>`` pattern that appears in place URLs
    - The ``@<lat>,<lon>`` pattern that appears in map URLs

    Args:
        url: A Google Maps URL string from which to parse coordinates.

    Returns:
        A tuple ``(latitude, longitude)`` if coordinates can be parsed;
        otherwise ``None``.
    """
    # Try to extract from !3d...!4d...
    match = re.search(r"!3d([-0-9.]+)!4d([-0-9.]+)", url)
    if match:
        lat, lon = map(float, match.groups())
        return lat, lon

    # Fallback: extract from @lat,lon
    match = re.search(r"@([-0-9.]+),([-0-9.]+)", url)
    if match:
        lat, lon = map(float, match.groups())
        return lat, lon

    return None
