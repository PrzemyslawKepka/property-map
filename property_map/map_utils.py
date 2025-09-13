import re

def extract_coordinates(url: str) -> tuple[float, float] | None:
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