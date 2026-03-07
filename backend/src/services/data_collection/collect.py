from nba_api.stats.endpoints import scoreboardv2
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import commonteamroster
from nba_api.stats.endpoints import teamgamelog
import pandas as pd
from services.data_collection.transformer_helper import TransformHelper
import logging
from nba_api.stats.endpoints import leagueleaders, teamdashboardbygeneralsplits, leaguegamefinder
from nba_api.stats.endpoints import leaguegamelog
from http.client import RemoteDisconnected
from services.data_collection.constants import Constants
import time as t


class CollectRawNBAData(TransformHelper, Constants):

    def __init__(self, **kwargs):
        self.date = kwargs["date_to_run"]
        self.season_id = self.create_season_id_year().get("season_id")
        self.season_year = self.create_season_id_year().get("season_year")
        self.headers = {
            'Host': 'stats.nba.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'x-nba-stats-origin': 'stats',
            'x-nba-stats-token': 'true',
            'Connection': 'keep-alive',
            'Referer': 'https://stats.nba.com/',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }

    def gather_and_import_nba_data(self, table_name = None, season_id: str = None, season_year: str = None):
        if season_id is None:
            season_id = self.season_id
        if season_year is None:
            season_year = self.season_year

        if table_name:
            logging.info(f"Gathering data for table: {table_name}")
            if table_name == "team_stats" or table_name == "team_roster":
                df = getattr(self, f"_get_{table_name}")(df_team_roster=self._get_team_info(), season_year=season_year, season_id=season_id)
            elif table_name == "player_stats":
                df = getattr(self, f"_get_{table_name}")(season_year=season_year, season_id=season_id)
            else:
                df = getattr(self, f"_get_{table_name}")()
            upper_case_table_name = table_name.upper()
            nba_data_dict = {
                getattr(self, upper_case_table_name): df,
            }
        else:
            logging.info("Gathering data for all tables")
            df_season = self._get_season_record(season_id=season_id)
            df_teams = self._get_team_info()
            df_players = self._get_players_info()
            df_teams_roster = self._get_team_roster(df_team_info=df_teams, season_year=season_year, season_id=season_id)
            df_team_logs = self._get_logs(season_year=season_year, pt_abbreviation="T")
            df_player_logs = self._get_logs(season_year=season_year, pt_abbreviation="P")

            nba_data_dict = {
                self.SEASON_RECORD: df_season,
                self.TEAMS_INFO: df_teams,
                self.TEAMS_ROSTER: df_teams_roster,
                self.PLAYERS_INFO: df_players,
                self.TEAM_STATS: df_team_logs,
                self.PLAYER_STATS: df_player_logs,
            }
        return nba_data_dict

    def _get_season_record(self, season_id: str) -> pd.DataFrame:

        season_year_dict = {"season_id": [int(season_id)]}
        df_from_dict = pd.DataFrame.from_dict(season_year_dict)

        logging.info("...Raw Season Info DF Generated")
        return df_from_dict

    def _get_games_played(self) -> pd.DataFrame:
        games = scoreboardv2.ScoreboardV2(day_offset=1, game_date=self.today)
        df_team_games_ids = games.get_data_frames()[0]

        return df_team_games_ids

    def _get_team_info(self) -> pd.DataFrame:
        df_team_info = pd.DataFrame(teams.get_teams())
        df_team_info = self.clean_dataframe(df_team_info)
        df_team_info["season_id"] = int(self.season_id)

        logging.info("...Raw Team Info DF Generated")
        return df_team_info

    def _get_team_roster(self, df_team_info: pd.DataFrame, season_year: str, season_id) -> pd.DataFrame:
        """Get team roster for each team in the season. 
        This is required to get the player ids for each team which is required to get the player stats and team stats for the season.
        """
        logging.info("Collecting team rosters for each team in the season")
        team_ids = df_team_info["id"].values.tolist()
        all_teams = self.transfrom_data(
            commonteamroster.CommonTeamRoster, team_ids, season=season_year, headers=self.headers
        )
        all_teams = self.clean_dataframe(all_teams)
        all_teams["team_id"] = all_teams["teamid"]
        df_team_rosters = all_teams[
            ["team_id", "player_id", "player", "age", "position"]
        ]
        df_team_rosters["season_id"] = int(season_id)

        logging.info("...Raw Team Roster DF Generated")
        return df_team_rosters

    def _get_team_logs(self, df_team_roster: pd.DataFrame, season_year: str, season_id: str) -> pd.DataFrame:
        team_ids = df_team_roster["team_id"].values.tolist()
        df_all_team_logs = self.transfrom_data(
            teamgamelog.TeamGameLog, team_ids, season=season_year
        )
        df_all_team_logs = self.clean_dataframe(df_all_team_logs)
        df_all_team_logs["teamid"] = df_all_team_logs["team_id"]
        df_all_team_logs["game_date"] = df_all_team_logs["game_date"].apply(
            self.convert_date_format
        )
        df_all_team_logs["season_id"] = int(season_id)
        df_all_team_logs

        logging.info("...Raw Team Game Logs DF Generated")
        return df_all_team_logs

    def _get_players_info(self) -> pd.DataFrame:
        df_players = pd.DataFrame(players.get_active_players())
        df_players = self.clean_dataframe(df_players)
        df_players = df_players.loc[df_players["is_active"] == True]
        df_players["season_id"] = int(self.season_id)

        logging.info("...Raw Player Info DF Generated")
        return df_players

    def _get_player_stats(self, season_year: str, season_id: str):
        leaders = leagueleaders.LeagueLeaders(season=season_year)
        df = leaders.get_data_frames()[0]
        df = self.clean_dataframe(df)
        df["season_id"] = int(season_id)
        df["date"] = self.date.strftime("%Y-%m-%d")
        df = df.dropna()
        logging.info("...Raw Player Averages DF Generated")
        return df


    def _get_logs(self, season_year: str, pt_abbreviation: str) -> pd.DataFrame:
        logging.info(f"Collecting logs for season: {season_year} and type: {pt_abbreviation}")
        # Retry loop to handle intermittent connection drops from the remote API
        max_retries = 5
        backoff_base = 2
        df_league_logs = None
        for attempt in range(1, max_retries + 1):
            try:
                league_logs = leaguegamelog.LeagueGameLog(
                    season=season_year,
                    player_or_team_abbreviation=pt_abbreviation,
                    headers=self.headers,
                    timeout=60,
                )
                df_league_logs = league_logs.get_data_frames()[0]
                break
            except RemoteDisconnected as e:
                logging.warning(
                    f"RemoteDisconnected on attempt {attempt}/{max_retries}: {e}. Retrying..."
                )
            except Exception as e:
                # Catch network-level and other transient errors and retry
                logging.warning(
                    f"Error fetching league game logs on attempt {attempt}/{max_retries}: {e}. Retrying..."
                )

            # if not returned, sleep with exponential backoff
            if attempt < max_retries:
                t.sleep(backoff_base ** attempt)
            else:
                logging.error(
                    f"Failed to fetch league game logs after {max_retries} attempts"
                )
                raise
        df_league_logs = self.clean_dataframe(df_league_logs)
        df_league_logs["game_date"] = df_league_logs["game_date"].apply(
            self.convert_date_format
        )
        logging.info("...Raw League Game Logs DF Generated")
        return df_league_logs
    
    def _get_team_stats(self, df_team_roster, season_year: str, season_id: str) -> pd.DataFrame:
        team_ids = df_team_roster["id"].values.tolist()
        df_all_team_logs = self.transfrom_data(
            teamdashboardbygeneralsplits.TeamDashboardByGeneralSplits,
            team_ids,
            season=season_year,
        )
        df_all_team_logs = self.clean_dataframe(df_all_team_logs)
        df_all_team_logs["season_id"] = int(season_id)
        df_all_team_logs["date"] = self.date.strftime("%Y-%m-%d")
        logging.info("...Raw Team Stats DF Generated")
        df_all_team_logs = df_all_team_logs.dropna()
        df_all_team_logs.drop(columns=["group_set", "group_value"], inplace=True)
        logging.info("...Raw Team Season Averages DF Generated")
        return df_all_team_logs

    def _get_team_matchups(self) -> pd.DataFrame:
        team_roster = self._get_team_info()
        team_roster_ids = pd.unique(team_roster["id"]).tolist()
        logging.info("Count of Team IDs: {}".format(len(team_roster_ids)))
        all_games = pd.DataFrame()
        logging.info(f"Team IDs for Matchups: {team_roster_ids}")
        logging.info("Count of Team IDs: {}".format(len(team_roster_ids)))

        for team_id in team_roster_ids:
            gamefinder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team_id)
            games = gamefinder.get_data_frames()[0]
            games = self.clean_dataframe(games)
            all_games = pd.concat([all_games, games], ignore_index=True)
            t.sleep(1)  # to avoid rate limiting
        logging.info("...Raw Team Matchups DF Generated")
        all_games = all_games.dropna()
        return all_games