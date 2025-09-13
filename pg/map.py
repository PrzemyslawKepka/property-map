import folium
import streamlit as st
from streamlit_folium import st_folium

from property_map.db import Database

st.header("Property map")

supabase = Database()
df_default_location = supabase.fetch_properties(table="default_location")
df_all = supabase.fetch_properties(table="all")

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
for index, row in df_all.iterrows():
    popup_text = f"""<b>{row["title"]}</b><br>
                    <b>price</b>: {row["price"]}<br>
                    <b>contract length</b>: {row["contract_length"]} months<br>
                    <b>date added</b>: {row["date_added"]}<br>
                    <b>description</b>: {row["description"]}<br>
                    <a href='{row["listing_url"]}' target='_blank'>Link</a><br>
                    <a href='{row["google_maps_url"]}' target='_blank'>Google Maps Link</a>"""
    popup = folium.Popup(html=popup_text, max_width=300)
    folium.Marker(
        location=[row["latitude"], row["longitude"]],
        popup=popup,
        tooltip=row["title"],
        icon=folium.Icon(
            color="blue" if row["contract_length"] <= 6 else "orange", icon="home"
        ),
    ).add_to(m)

st_folium(m, width=800, height=600)

st.dataframe(df_all)
