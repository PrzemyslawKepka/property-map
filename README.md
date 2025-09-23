### Overview
The app was created as a helper tool in a process of finding an apartment to rent, which often can be a quite mundane endeavour. Depending on the website used to find the apartments, keeping a track of all the potential apartments might be hard if there's no map available by default, so that tool aims to facilitate that problem by allowing to save any listings and display them on the map.

Core features:
- Save apartment listings via a simple form
- Visualize saved listings on an interactive map

<img src="https://github.com/PrzemyslawKepka/property-map/blob/main/images/property_map.png" />

So as a result, the map allows an easier navigation through all the listings that you want to keep an eye on, which ultimately should lead to a smoother process of finding an ideal place.

### Tech stack

- Streamlit for the UI and page navigation
- Supabase (PostgreSQL + API) for persistence
- Folium for map rendering
- Python 3.11

### Installation

Below are the steps to run the app locally on any computer:

Prerequisites:
- Python 3.11 installed
- A Supabase instance (with tables and schema described in the Data storage section)

1) Install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2) Configure environment

Create a `.env` file in the project root with your Supabase credentials:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

3) Run the app

```bash
streamlit run app.py
```

### Data storage

The app uses Supabase for persistence and relies on two tables:
  - `main listings table`: Stores all properties added via the form page. All rows in this table are shown on the map.
  - `default location table`: Stores a single "home" or reference location used as the map's starting point. It is rendered with a different icon (currently a heart). This table is managed manually in Supabase and is optional.

Configure the schema and exact table names in `property_map/db.py` via `SCHEMA`, `DATA_TABLE`, and `DEFAULT_LOCATION_TABLE` variables.

### App usage

#### Pages

- Property form: Add a new listing by pasting a listing URL and a Google Maps URL. Coordinates are extracted automatically from the Google Maps URL.
- Property map: Browse all saved listings on a Folium map. Clicking a marker shows a popup with details and links.

#### Adding a listing

- Provide title, price, contract length (months), has a desk (Yes/No), date added, and an optional description.
- Paste a Google Maps URL. The app supports patterns like `!3d<lat>!4d<lon>` and `@<lat>,<lon>`.
- Submit to save the listing to Supabase.

