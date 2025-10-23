import pandas as pd
import time as t
from datetime import datetime
from nba_api.stats.endpoints import teamdashboardbygeneralsplits


class TransformHelper:
    def transfrom_data(self, api, *args, **kwargs) -> pd.DataFrame:
        ids = args[0]
        tran_empty_array = []
        for id in ids:
            try:
                df = api(id, **kwargs).get_data_frames()[0]
                if api == teamdashboardbygeneralsplits.TeamDashboardByGeneralSplits:
                    df["team_id"] = id
                tran_empty_array.append(df)
                t.sleep(1)  # to avoid rate limiting
            except Exception as e:
                print(f"Error fetching data for ID {id}: {e}")
                continue

        return pd.concat(tran_empty_array)

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
        date_object = datetime.strptime(date_string, "%b %d, %Y")
        formatted_date = date_object.strftime("%Y-%m-%d")

        return formatted_date

    def clean_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.rename(columns=lambda col: col.lower())
        return df
