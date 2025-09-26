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

from property_map.db import Database

if "is_mobile" not in st.session_state:
    st.session_state["is_mobile"] = False


# Get user agent and screen width with error handling
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

except (TypeError, AttributeError):
    # Handle cases where JavaScript returns invalid values during loading
    st.session_state["screen_width"] = 375  # Default mobile width

# Set responsive dimensions
if st.session_state["is_mobile"]:
    # Use actual screen width minus some padding for mobile
    screen_width = st.session_state.get("screen_width", 375)
    map_width = max(
        320, min(screen_width - 20, 600)
    )  # Min 320px, max 600px, with 20px padding
    map_height = int(
        map_width * 1.2
    )  # Taller aspect ratio (5:6) for better map visibility
    popup_width = max(150, min(map_width - 50, 200))  # Responsive popup width
    popup_text_font_size = "12px"
    popup_image_width = "150"
    popup_image_height = "113"
else:
    map_width = 800  # Slightly wider for desktop too
    map_height = 600  # Taller for desktop as well
    popup_width = 300
    popup_text_font_size = "14px"
    popup_image_width = "200"
    popup_image_height = "150"

# loading the data
supabase = Database()
df_default_location = supabase.fetch_properties(table="default_location")
df_all = supabase.fetch_properties(table="all")

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

# price filter
price_filter = st.sidebar.slider(
    "Price filter (in THB)",
    min_value=df_all["price"].min(),
    max_value=df_all["price"].max(),
    value=(df_all["price"].min(), df_all["price"].max()),
    step=1000,
)
# status flag from numeric to descriptive
flag_to_description = {
    0: "Full",
    1: "Free rooms",
    2: "TBD",
}
df_all["mid_Sep_flag"] = df_all["mid_Sep_flag"].map(flag_to_description)
# status filter
status_filter = st.sidebar.multiselect(
    "Status filter",
    options=df_all["mid_Sep_flag"].unique(),
    default=df_all["mid_Sep_flag"].unique(),
)

# filter the data
price_mask = (df_all["price"] >= price_filter[0]) & (df_all["price"] <= price_filter[1])
status_mask = df_all["mid_Sep_flag"].isin(status_filter)
filtered_df = df_all[price_mask & status_mask]

# Main display
st.header("CM monthly rentals")
st.markdown("Status as of September 2025")

# Map
# get the median latitude and longitude
median_latitude = df_all["latitude"].median()
median_longitude = df_all["longitude"].median()
start_coords = [median_latitude, median_longitude]
m = folium.Map(location=start_coords, zoom_start=13)

# Add markers for each row in the DataFrame
for index, row in filtered_df.iterrows():
    current_description = "" if not row["mid_Sep_status"] else row["mid_Sep_status"]
    popup_text = f"""<div style="font-size: {popup_text_font_size};">
                    <b>{row["title"]}</b><br>
                    <b>monthly price</b>: {row["price"]} THB <br>
                    <b>description</b>: {row["description"]}<br>
                    <b>mid-September status</b>: {current_description} <br>
                    <a href='{row["listing_url"]}' target='_blank'>Link</a><br>
                    <a href='{row["google_maps_url"]}' target='_blank'>Google Maps Link</a><br>
                    <img src="{row["image_url"]}" width="{popup_image_width}" height="{popup_image_height}">
                    </div>
                    """
    popup = folium.Popup(html=popup_text, max_width=popup_width)
    tooltip_text = f"""<b>{row["title"]}</b><br>
                    <img src="{row["image_url"]}" width="100" height="75">
                    """

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

st.dataframe(
    filtered_df[cols_to_display].sort_values(by="title", ascending=True),
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
)

st.markdown(
    """
    * Please note that the availability was checked mostly
        around 15th-17th September 2025, so it could have changed sice then
        and should be re-checked"""
)
