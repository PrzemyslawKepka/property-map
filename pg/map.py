"""Streamlit page that renders an interactive Folium map of properties.

The page reads rows from Supabase via the ``Database`` helper, places a red
marker for the default location, and adds color-coded markers for each
property (blue for contract length <= 6 months, orange otherwise).
"""

import folium
import streamlit as st
from streamlit_folium import st_folium
from streamlit_javascript import st_javascript
from user_agents import parse

from property_map.config import (
    CACHE_TTL,
    IMAGE_CONFIG,
    MAP_CONFIG,
    PERFORMANCE_CONFIG,
    RESPONSIVE_CONFIG,
)
from property_map.db import Database

# Initialize session state for device detection (only once)
if "device_detected" not in st.session_state:
    st.session_state["device_detected"] = False
    st.session_state["is_mobile"] = False
    st.session_state["screen_width"] = 800  # Default desktop width

# Get user agent and screen width with error handling (only if not detected yet)
if not st.session_state["device_detected"]:
    try:
        user_agent_string = st_javascript("window.navigator.userAgent")
        screen_width = st_javascript("window.innerWidth")

        # Check if we got valid values (not 0 or None during loading)
        if user_agent_string and isinstance(user_agent_string, str):
            user_agent = parse(user_agent_string)
            if user_agent.is_mobile:
                st.session_state["is_mobile"] = True

        # Get screen width for responsive sizing
        if screen_width and isinstance(screen_width, (int, float)) and screen_width > 0:
            st.session_state["screen_width"] = int(screen_width)
        else:
            # Fallback to default mobile width if detection fails
            st.session_state["screen_width"] = 375

        st.session_state["device_detected"] = True

    except (TypeError, AttributeError):
        # Handle cases where JavaScript returns invalid values during loading
        st.session_state["screen_width"] = 375  # Default mobile width
        st.session_state["device_detected"] = True

# Set responsive dimensions using configuration
if st.session_state["is_mobile"]:
    # Use actual screen width minus some padding for mobile
    screen_width = st.session_state.get(
        "screen_width", RESPONSIVE_CONFIG["mobile_screen_width"]
    )
    map_width = max(
        MAP_CONFIG["mobile_min_width"],
        min(
            screen_width - MAP_CONFIG["mobile_padding"], MAP_CONFIG["mobile_max_width"]
        ),
    )
    map_height = int(map_width * MAP_CONFIG["mobile_aspect_ratio"])
    popup_width = max(150, min(map_width - 50, IMAGE_CONFIG["popup_width_mobile"]))
    popup_text_font_size = RESPONSIVE_CONFIG["font_size_mobile"]
    popup_image_width = IMAGE_CONFIG["popup_image_width_mobile"]
    popup_image_height = IMAGE_CONFIG["popup_image_height_mobile"]
else:
    map_width = MAP_CONFIG["desktop_width"]
    map_height = MAP_CONFIG["desktop_height"]
    popup_width = IMAGE_CONFIG["popup_width_desktop"]
    popup_text_font_size = RESPONSIVE_CONFIG["font_size_desktop"]
    popup_image_width = IMAGE_CONFIG["popup_image_width_desktop"]
    popup_image_height = IMAGE_CONFIG["popup_image_height_desktop"]


# Initialize data loading with caching
@st.cache_data(ttl=CACHE_TTL["data"])  # Cache for configured duration
def load_property_data():
    """Load property data from database with caching."""
    supabase = Database()
    df_default_location = supabase.fetch_properties(table="default_location")
    df_all = supabase.fetch_properties(table="all")
    return df_default_location, df_all


# Load data with caching
df_default_location, df_all = load_property_data()

# Sidebar
# logo
st.sidebar.image("images/app_logo.png", width=100)
st.sidebar.divider()

# info text
st.sidebar.markdown("""
Usage:
* Map: click on the property to see the details
* Table: browse the details of all properties listed
* Price filter: filter by price
* Status filter: filter by status
""")
st.sidebar.divider()


# Cache data processing to avoid repeated transformations
@st.cache_data
def process_property_data(df_all):
    """Process property data with status mapping."""
    # Create a copy to avoid modifying cached data
    df_processed = df_all.copy()

    # status flag from numeric to descriptive
    flag_to_description = {
        0: "Full",
        1: "Free rooms",
        2: "TBD",
    }
    df_processed["mid_Sep_flag"] = df_processed["mid_Sep_flag"].map(flag_to_description)

    return df_processed


# Process data with caching
df_processed = process_property_data(df_all)

# Initialize session state for filters
if "price_filter" not in st.session_state:
    st.session_state["price_filter"] = (
        df_processed["price"].min(),
        df_processed["price"].max(),
    )
if "status_filter" not in st.session_state:
    st.session_state["status_filter"] = df_processed["mid_Sep_flag"].unique().tolist()

# price filter
price_filter = st.sidebar.slider(
    "Price filter (in THB)",
    min_value=df_processed["price"].min(),
    max_value=df_processed["price"].max(),
    value=st.session_state["price_filter"],
    step=1000,
    key="price_slider",
)

# status filter
status_filter = st.sidebar.multiselect(
    "Status filter",
    options=df_processed["mid_Sep_flag"].unique(),
    default=st.session_state["status_filter"],
    key="status_multiselect",
)

# Update session state
st.session_state["price_filter"] = price_filter
st.session_state["status_filter"] = status_filter

# filter the data
price_mask = (df_processed["price"] >= price_filter[0]) & (
    df_processed["price"] <= price_filter[1]
)
status_mask = df_processed["mid_Sep_flag"].isin(status_filter)
filtered_df = df_processed[price_mask & status_mask]

# Main display
st.header("CM monthly rentals")
st.markdown("Status as of September 2025")


# Cache map creation to avoid recreating on every interaction
@st.cache_data
def create_base_map(df_all):
    """Create base map with center coordinates."""
    median_latitude = df_all["latitude"].median()
    median_longitude = df_all["longitude"].median()
    start_coords = [median_latitude, median_longitude]
    return folium.Map(location=start_coords, zoom_start=MAP_CONFIG["default_zoom"])


# Create base map
m = create_base_map(df_all)


# Optimize image loading with lazy loading and error handling
def create_optimized_popup(
    row, popup_text_font_size, popup_width, popup_image_width, popup_image_height
):
    """Create popup with optimized image loading."""
    current_description = "" if not row["mid_Sep_status"] else row["mid_Sep_status"]

    # Use lazy loading for images and add error handling based on configuration
    lazy_loading = 'loading="lazy"' if IMAGE_CONFIG["lazy_loading"] else ""
    error_handling = (
        "onerror=\"this.style.display='none'\""
        if IMAGE_CONFIG["error_handling"]
        else ""
    )

    popup_text = f"""<div style="font-size: {popup_text_font_size};">
                    <b>{row["title"]}</b><br>
                    <b>monthly price</b>: {row["price"]} THB <br>
                    <b>description</b>: {row["description"]}<br>
                    <b>mid-September status</b>: {current_description} <br>
                    <a href='{row["listing_url"]}' target='_blank'>Link</a><br>
                    <a href='{row["google_maps_url"]}' target='_blank'>Google Maps Link</a><br>
                    <img src="{row["image_url"]}" 
                         width="{popup_image_width}" 
                         height="{popup_image_height}"
                         {lazy_loading}
                         {error_handling}>
                    </div>
                    """
    return folium.Popup(html=popup_text, max_width=popup_width)


def create_optimized_tooltip(row):
    """Create tooltip with optimized image loading."""
    lazy_loading = 'loading="lazy"' if IMAGE_CONFIG["lazy_loading"] else ""
    error_handling = (
        "onerror=\"this.style.display='none'\""
        if IMAGE_CONFIG["error_handling"]
        else ""
    )

    tooltip_text = f"""<b>{row["title"]}</b><br>
                    <img src="{row["image_url"]}" 
                         width="100" 
                         height="75"
                         {lazy_loading}
                         {error_handling}>
                    """
    return tooltip_text


# Add markers for each row in the DataFrame (only if filtered data changed)
if PERFORMANCE_CONFIG["enable_marker_caching"] and (
    "last_filtered_count" not in st.session_state
    or st.session_state["last_filtered_count"] != len(filtered_df)
):
    # Clear existing markers (if any)
    for key in list(st.session_state.keys()):
        if key.startswith("marker_"):
            del st.session_state[key]

    # Add new markers
    for index, row in filtered_df.iterrows():
        popup = create_optimized_popup(
            row,
            popup_text_font_size,
            popup_width,
            popup_image_width,
            popup_image_height,
        )
        tooltip_text = create_optimized_tooltip(row)

        # Map the descriptive text back to numeric values for color coding
        description_to_flag = {"Full": 0, "Free rooms": 1, "TBD": 2}
        numeric_flag = description_to_flag[row["mid_Sep_flag"]]
        status_flags = {0: "red", 1: "green", 2: "orange"}
        icon_color = status_flags[numeric_flag]

        folium.Marker(
            location=[row["latitude"], row["longitude"]],
            popup=popup,
            tooltip=None if st.session_state["is_mobile"] else tooltip_text,
            icon=folium.Icon(
                color=icon_color,
                icon="home",
            ),
        ).add_to(m)

    # Update marker count in session state
    st.session_state["last_filtered_count"] = len(filtered_df)


st_folium(m, width=map_width, height=map_height)

st.markdown(
    """
    :green[Green] - Availability confirmed |
    :orange[Orange] - Availability not checked or not confirmed (TBD) |
    :red[Red] - Confirmed as fully booked"""
)

# st.divider()

cols_to_display = [
    "image_url",
    "title",
    "listing_url",
    "google_maps_url",
    "price",
    "description",
    "mid_Sep_status",
    "mid_Sep_flag",
]


# Cache dataframe sorting to avoid repeated operations
@st.cache_data
def sort_dataframe(df, cols_to_display):
    """Sort dataframe by title."""
    return df[cols_to_display].sort_values(by="title", ascending=True)


# Display optimized dataframe
if PERFORMANCE_CONFIG["enable_dataframe_sorting_cache"]:
    sorted_df = sort_dataframe(filtered_df, cols_to_display)
else:
    sorted_df = filtered_df[cols_to_display].sort_values(by="title", ascending=True)

st.dataframe(
    sorted_df,
    column_config={
        "image_url": st.column_config.ImageColumn("Image", width="small"),
        "title": st.column_config.Column("Title"),
        "listing_url": st.column_config.LinkColumn("Listing URL", width="medium"),
        "google_maps_url": st.column_config.LinkColumn(
            "Google Maps URL", width="medium"
        ),
        "price": st.column_config.NumberColumn("Price (in THB)", width=8),
        "mid_Sep_status": st.column_config.Column(
            "Mid-September Description", width="medium"
        ),
        "mid_Sep_flag": st.column_config.Column("Mid-September Status", width="small"),
    },
    use_container_width=True,  # Better responsive behavior
    hide_index=True,  # Hide index for cleaner look
)

st.markdown(
    """
    * Please note that the availability was checked mostly
        around 15th-17th September 2025, so it could have changed sice then
        and should be re-checked"""
)
