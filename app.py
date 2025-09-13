import streamlit as st

st.set_page_config(layout="wide")

form_page = st.Page("pg/form.py", title="Property form", icon="🏠")
map_page = st.Page("pg/map.py", title="Property map", icon="🏠")

# Create the navigation
pg = st.navigation([form_page, map_page])

# Run the selected page
pg.run()
