"""Streamlit page with a form for adding a new property listing.

The form collects listing metadata, parses coordinates from a Google Maps
URL, and inserts a new row into Supabase using the ``Database`` helper.
"""

import streamlit as st

from property_map.db import Database
from property_map.map_utils import extract_coordinates

st.header("Add a new listing")

with st.form("property_form", clear_on_submit=True):
    title = st.text_input("Title")
    listing_url = st.text_input("URL (e.g. facebook post)")
    google_maps_url = st.text_input("Google maps URL")
    price = st.number_input("Price (Thai Baht)", min_value=0, max_value=20000)
    contract_length = st.number_input(
        "Contract length (months)", min_value=0, max_value=12
    )
    has_a_desk = st.pills("Has a desk", options=["Yes", "No"])
    date_added = st.date_input("Date added")
    description = st.text_area(
        "Description", placeholder="Short description (optional)"
    )

    submitted = st.form_submit_button("Add to map")

    if submitted:
        lat, lon = extract_coordinates(google_maps_url)
        desk_flag = 1 if has_a_desk == "Yes" else 0
        supabase = Database()
        supabase.insert_property(
            title,
            listing_url,
            google_maps_url,
            lat,
            lon,
            price,
            contract_length,
            desk_flag,
            date_added,
            description,
        )
        st.success(
            f"Listing added to map: {title} ({lat}, {lon}) {price} {contract_length} {desk_flag} {description}"
        )
