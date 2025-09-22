import os
from datetime import date

import pandas as pd
from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()  # Load environment variables from .env file

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SCHEMA = "public"
DATA_TABLE = "properties"
DEFAULT_LOCATION_TABLE = "default_location"


class Database:
    """Lightweight data-access layer over a Supabase table.

    The class encapsulates a Supabase Python client and exposes the minimal
    operations used by the app:

    - Insert a row into the ``properties`` table
    - Read rows from either the ``properties`` table (``table='all'``)
      or from the ``default_location`` table (``table='default_location'``)

    Attributes:
        url: Supabase project URL.
        key: Supabase anon/service key.
        schema: Database schema to operate on (defaults to ``public``).
        data_table: Name of the properties data table.
        default_location_table: Name of the table with the default map location.
        client: Initialized Supabase client instance.
    """

    def __init__(
        self,
        supabase_url: str = SUPABASE_URL,
        supabase_key: str = SUPABASE_KEY,
        schema: str = SCHEMA,
        data_table: str = DATA_TABLE,
        default_location_table: str = DEFAULT_LOCATION_TABLE,
    ) -> None:
        """Initialize the client and configuration.

        Args:
            supabase_url: Supabase project URL. Defaults to ``SUPABASE_URL``.
            supabase_key: Supabase key. Defaults to ``SUPABASE_KEY``.
            schema: Database schema to use. Defaults to ``public``.
            data_table: Name of the properties table.
            default_location_table: Name of the default location table.
        """
        self.url = supabase_url
        self.key = supabase_key
        self.schema = schema
        self.data_table = data_table
        self.default_location_table = default_location_table
        self.client: Client = create_client(self.url, self.key)

    def insert_property(
        self,
        title: str,
        listing_url: str,
        google_maps_url: str,
        latitude: float,
        longitude: float,
        price: int,
        contract_length: int,
        has_a_desk: int,
        date_added: date,
        description: str,
    ) -> None:
        """Insert a single property row.

        Args:
            title: Human-readable title of the listing.
            listing_url: External listing URL (e.g., Facebook).
            google_maps_url: Google Maps URL pointing to the place.
            latitude: Latitude in decimal degrees.
            longitude: Longitude in decimal degrees.
            price: Price in Thai Baht.
            contract_length: Contract length in months.
            has_a_desk: 1 if a desk is available, 0 otherwise.
            date_added: Date when the listing was added.
            description: Optional free-text description.

        """
        (
            self.client.from_(self.data_table)
            .insert(
                [
                    {
                        "title": title,
                        "listing_url": listing_url,
                        "google_maps_url": google_maps_url,
                        "latitude": latitude,
                        "longitude": longitude,
                        "price": price,
                        "contract_length": contract_length,
                        "has_a_desk": has_a_desk,
                        "date_added": date_added.strftime("%Y-%m-%d"),
                        "description": description,
                    }
                ]
            )
            .execute()
        )
        return None

    def fetch_properties(self, table: str) -> pd.DataFrame:
        """Fetch properties/default location rows as a pandas DataFrame.

        Args:
            table: ``"all"`` to read from the properties table, or
                ``"default_location"`` to read the single default location.

        Returns:
            A ``pandas.DataFrame`` with the selected rows.

        Raises:
            ValueError: If ``table`` is not one of the supported options.
        """
        if table == "all":
            table = self.data_table
        elif table == "default_location":
            table = self.default_location_table
        else:
            raise ValueError(f"Invalid table: {table}")
        response = self.client.table(table).select("*").execute()
        data = response.data
        df = pd.DataFrame(data)
        return df
