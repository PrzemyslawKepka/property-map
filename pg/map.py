"""Streamlit page that renders an interactive Folium map of properties.

The page reads rows from Supabase via the ``Database`` helper, places a red
marker for the default location, and adds color-coded markers for each
property (blue for contract length <= 6 months, orange otherwise).
"""

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from property_map.db import Database

st.header("CM monthly rentals")
st.markdown("Status as of September 2025")

supabase = Database()
df_default_location = supabase.fetch_properties(table="default_location")
df_all = supabase.fetch_properties(table="all")
price_filter = st.sidebar.slider(
    "Price filter",
    min_value=df_all["price"].min(),
    max_value=df_all["price"].max(),
    value=(df_all["price"].min(), df_all["price"].max()),
    step=1000,
)
# Create status filter options after mapping
flag_to_description = {
    0: "Full",
    1: "Free rooms",
    2: "TBD",
}
df_all["mid_Sep_flag"] = df_all["mid_Sep_flag"].map(flag_to_description)

status_filter = st.sidebar.multiselect(
    "Status filter",
    options=df_all["mid_Sep_flag"].unique(),
    default=df_all["mid_Sep_flag"].unique(),
)
start_coords = df_default_location[["latitude", "longitude"]].iloc[0].tolist()
m = folium.Map(location=start_coords, zoom_start=13)

# Add marker for default location
for index, row in df_default_location.iterrows():
    folium.Marker(
        location=[row["latitude"], row["longitude"]],
        tooltip=row["title"],
        icon=folium.Icon(color="red", icon="heart"),
    ).add_to(m)

# Add markers for each row in the DataFrame
price_mask = (df_all["price"] >= price_filter[0]) & (df_all["price"] <= price_filter[1])

# Handle multiselect status filter
if status_filter:  # If any status options are selected
    status_mask = df_all["mid_Sep_flag"].isin(status_filter)
else:  # If no status options are selected, show nothing
    status_mask = pd.Series([False] * len(df_all), index=df_all.index)

filtered_df = df_all[price_mask & status_mask]

for index, row in filtered_df.iterrows():
    current_description = "" if not row["mid_Sep_status"] else row["mid_Sep_status"]
    popup_text = f"""<b>{row["title"]}</b><br>
                    <b>monthly price</b>: {row["price"]} THB <br>
                    <b>description</b>: {row["description"]}<br>
                    <b>mid-September status</b>: {current_description} <br>
                    <a href='{row["listing_url"]}' target='_blank'>Link</a><br>
                    <a href='{row["google_maps_url"]}' target='_blank'>Google Maps Link</a>"""
    popup = folium.Popup(html=popup_text, max_width=300)

    # Map the descriptive text back to numeric values for color coding
    description_to_flag = {"Full": 0, "Free rooms": 1, "TBD": 2}
    numeric_flag = description_to_flag[row["mid_Sep_flag"]]
    status_flags = {0: "red", 1: "green", 2: "orange"}
    icon_color = status_flags[numeric_flag]

    folium.Marker(
        location=[row["latitude"], row["longitude"]],
        popup=popup,
        tooltip=row["title"],
        icon=folium.Icon(
            color=icon_color,
            icon="home",
        ),
    ).add_to(m)


st_folium(m, width=800, height=600)

st.markdown(
    """
    :green[Green] - Availability confirmed |
    :orange[Orange] - Availability not confirmed or partially confirmed |
    :red[Red] - Confirmed as fully booked"""
)

cols_to_display = [
    "title",
    "listing_url",
    "google_maps_url",
    "price",
    "description",
    "mid_Sep_status",
    "mid_Sep_flag",
]

st.dataframe(
    filtered_df[cols_to_display],
    column_config={
        "title": st.column_config.Column("Title"),
        "listing_url": st.column_config.LinkColumn("Listing URL", width="small"),
        "google_maps_url": st.column_config.LinkColumn(
            "Google Maps URL", width="small"
        ),
        "price": st.column_config.NumberColumn("Price", width=5),
        "mid_Sep_status": st.column_config.Column(
            "Mid-September Description", width="medium"
        ),
        "mid_Sep_flag": st.column_config.Column("Mid-September Status", width="small"),
    },
)
