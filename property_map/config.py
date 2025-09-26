"""Configuration settings for the Property Map application.

This module contains performance and caching configurations optimized for
server deployment with limited resources.
"""

# Caching TTL settings (in seconds)
CACHE_TTL = {
    "data": 300,  # 5 minutes for property data
    "client": 3600,  # 1 hour for database client
    "processing": 1800,  # 30 minutes for data processing
}

# Map configuration
MAP_CONFIG = {
    "default_zoom": 13,
    "mobile_aspect_ratio": 1.2,
    "desktop_width": 800,
    "desktop_height": 600,
    "mobile_min_width": 320,
    "mobile_max_width": 600,
    "mobile_padding": 20,
}

# Image optimization settings
IMAGE_CONFIG = {
    "lazy_loading": True,
    "error_handling": True,
    "popup_width_desktop": 300,
    "popup_width_mobile": 200,
    "popup_image_width_desktop": "200",
    "popup_image_height_desktop": "150",
    "popup_image_width_mobile": "150",
    "popup_image_height_mobile": "113",
}

# Performance settings
PERFORMANCE_CONFIG = {
    "enable_marker_caching": True,
    "enable_dataframe_sorting_cache": True,
    "enable_session_state_persistence": True,
    "min_filtered_count_for_rerender": 1,
    "debug_mode": False,  # Set to True to enable debug logging
}

# Responsive design settings
RESPONSIVE_CONFIG = {
    "font_size_desktop": "15px",
    "font_size_mobile": "13px",
    "default_screen_width": 800,
    "mobile_screen_width": 375,
}
