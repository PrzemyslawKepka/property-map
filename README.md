### Overview
The app was created as a helper tool in a process of finding an apartment to rent, which often can be a quite mundane process. Depending on the website used to find the apartments, keeping a track of all the potential apartments might be hard if there's no map available by default, so that tool aims to facilitate that problem by allowing to save any listings and display them on the map.

So there are two basic functionalities:
- Saving apartment listings through a simple form
- Visualizing saved listings on an interactive map

<img src="https://github.com/PrzemyslawKepka/property-map/blob/main/images/property_map.png" />

### Tech stack

- Streamlit for the UI and page navigation
- Folium for the map rendering
- Supabase (PostgreSQL + API) for persistence
- Python 3.11

### Installation

Below are the steps to run the app locally on any computer:

Prerequisites:
- Python installed on the computer
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

- Supabase schema `public` with two tables used by the app:
  - `properties`: main listings table
  - `default_location`: a single reference location to center the map

Table names and schema can of course be changed, but the code must be updated accordingly.

### App usage

#### Pages

- Property form: add a new listing by pasting a listing URL and a Google Maps URL. The app extracts coordinates automatically from the Google Maps URL.
- Property map: browse all saved listings on a Folium map. Clicking a marker shows a popup with details and links.

#### Adding a listing

- Title, price, contract length (months), has a desk (Yes/No), date added, and an optional description.
- Paste a Google Maps URL. The app supports patterns like `!3d<lat>!4d<lon>` and `@<lat>,<lon>`.
- Submit to save the listing to Supabase.

