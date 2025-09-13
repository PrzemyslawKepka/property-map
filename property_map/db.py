import os
from datetime import date
from typing import Any, Dict

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
    """Thin wrapper around Supabase client for the `properties` table."""

    def __init__(
        self,
        supabase_url: str = SUPABASE_URL,
        supabase_key: str = SUPABASE_KEY,
        schema: str = SCHEMA,
        data_table: str = DATA_TABLE,
        default_location_table: str = DEFAULT_LOCATION_TABLE,
    ) -> None:
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
    ) -> Dict[str, Any]:
        """Insert a single property row; returns inserted row as dict.

        has_a_desk should be 0/1 to match SMALLINT.
        """
        response = (
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
        return response

    def fetch_properties(self, table: str) -> pd.DataFrame:
        """Fetch all properties as a DataFrame."""
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
