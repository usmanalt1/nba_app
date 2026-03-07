import logging
import pandas as pd
import requests
import time as t
from datetime import datetime
from http.client import RemoteDisconnected
from nba_api.stats.endpoints import teamdashboardbygeneralsplits


class TransformHelper:
    def transfrom_data(self, api, *args, **kwargs) -> pd.DataFrame:
        ids = args[0]
        tran_empty_array = []
        logger = logging.getLogger(__name__)
        for id in ids:
            max_retries = 5
            for attempt in range(1, max_retries + 1):
                try:
                    df = api(id, **kwargs).get_data_frames()[0]
                    if api == teamdashboardbygeneralsplits.TeamDashboardByGeneralSplits:
                        df["team_id"] = id
                    tran_empty_array.append(df)
                    t.sleep(1)  # to avoid rate limiting
                    break
                except (RemoteDisconnected, requests.exceptions.RequestException) as e:
                    logger.warning(
                        f"Transient error fetching data for ID {id} on attempt {attempt}/{max_retries}: {e}"
                    )
                except Exception as e:
                    logger.warning(f"Error fetching data for ID {id} on attempt {attempt}/{max_retries}: {e}")

                if attempt < max_retries:
                    t.sleep(2 ** attempt)
                else:
                    logger.error(f"Failed to fetch data for ID {id} after {max_retries} attempts")
                    break

        if len(tran_empty_array) == 0:
            return pd.DataFrame()

        return pd.concat(tran_empty_array, ignore_index=True)

    def create_season_id_year(self) -> str:
        def get_season_year() -> str:
            current_datetime = self.date
            current_season_year = current_datetime.year
            if current_datetime.month <= 9:
                current_season_year -= 1

            return current_season_year

        current_season_year = get_season_year()

        season_id = "{}0{}".format(
            str(current_season_year)[2:], str(current_season_year + 1)[2:]
        )
        season_year = "{}-{}".format(
            current_season_year, str(current_season_year + 1)[2:]
        )

        season_dict = {"season_id": season_id, "season_year": season_year}

        return season_dict

    def convert_date_format(self, date_string) -> str:
        try:
            if date_string is None:
                return None
            
            date_obj = pd.to_datetime(date_string, errors="coerce")
            if pd.isna(date_obj):
                print(f"Error converting date string '{date_string}': unrecognized format")
                raise ValueError(f"Unrecognszed date format: {date_string}")
            formatted_date = date_obj.strftime("%Y-%m-%d")
        except Exception as e:
            print(f"Error converting date string '{date_string}': {e}")
            formatted_date = None

        return formatted_date

    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.rename(columns=lambda col: col.lower())
        return df
