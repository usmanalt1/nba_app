from nba_api.stats.endpoints import scoreboardv2
from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import commonteamroster
from nba_api.stats.endpoints import teamgamelog
import pandas as pd
from data.transformer_helper import TransformHelper
import logging
from nba_api.stats.endpoints import leagueleaders, teamdashboardbygeneralsplits
from data.constants import Constants
class CollectRawNBAData(TransformHelper, Constants):
 
    def __init__(self, **kwargs):
        self.date = kwargs["date_to_run"]
        self.season_id = self.create_season_id_year().get("season_id")
        self.season_year =  self.create_season_id_year().get("season_year")

    def gather_and_import_nba_data(self):
        df_season = self._get_season_year()
        df_teams = self._get_team_info()
        df_players = self._get_players()
        df_teams_roster = self._get_team_roster(df_teams)
        df_team_stats = self.get_team_season_averages(df_teams)
        df_player_stats = self._get_player_season_averages()

        nba_data_dict = {
            self.SEASON_RECORD: df_season,
            self.TEAMS_INFO: df_teams,
            self.TEAMS_ROSTER: df_teams_roster,
            self.PLAYERS_INFO: df_players,
            self.TEAM_STATS: df_team_stats,
            self.PLAYER_STATS: df_player_stats,
        }
        return nba_data_dict

    def _get_season_year(self) -> pd.DataFrame:

        season_year_dict = {"season_id": [int(self.season_id)]}
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
 
    def _get_team_roster(self, df_team_info: pd.DataFrame) -> pd.DataFrame:
        team_ids = df_team_info["id"].values.tolist()
        all_teams = self.transfrom_data(commonteamroster.CommonTeamRoster, team_ids, season=self.season_year)
        all_teams = self.clean_dataframe(all_teams)
        all_teams["team_id"] = all_teams["teamid"] 
        df_team_rosters = all_teams[["team_id", "player_id", "player", "age", "position"]]
        df_team_rosters["season_id"] = int(self.season_id)

        logging.info("...Raw Team Roster DF Generated")
        return df_team_rosters
    
    def _get_team_logs(self, df_team_roster: pd.DataFrame) -> pd.DataFrame:
        team_ids = df_team_roster["team_id"].values.tolist()
        df_all_team_logs = self.transfrom_data(teamgamelog.TeamGameLog, team_ids, season=self.season_year)
        df_all_team_logs = self.clean_dataframe(df_all_team_logs)
        df_all_team_logs["teamid"] = df_all_team_logs["team_id"]
        df_all_team_logs["game_date"] = df_all_team_logs["game_date"].apply(self.convert_date_format)
        df_all_team_logs["season_id"] = int(self.season_id)

        logging.info("...Raw Team Game Logs DF Generated")
        return df_all_team_logs
    
    def _get_players(self) -> pd.DataFrame:
        df_players = pd.DataFrame(players.get_active_players())
        df_players = self.clean_dataframe(df_players)
        df_players = df_players.loc[df_players["is_active"] == True]
        df_players["season_id"] = int(self.season_id)

        logging.info("...Raw Player Info DF Generated")
        return df_players
    
    def _get_player_season_averages(self):
        leaders = leagueleaders.LeagueLeaders(season=self.season_year)
        df = leaders.get_data_frames()[0]
        df = self.clean_dataframe(df)
        df["season_id"] = int(self.season_id)
        df["date"] = self.date.strftime("%Y-%m-%d")
        df = df.dropna()
        logging.info("...Raw Player Info DF Generated")
        return df
    
    def get_team_season_averages(self, df_team_roster):
        team_ids = df_team_roster["id"].values.tolist()
        df_all_team_logs = self.transfrom_data(teamdashboardbygeneralsplits.TeamDashboardByGeneralSplits, team_ids, season=self.season_year)
        df_all_team_logs = self.clean_dataframe(df_all_team_logs)
        df_all_team_logs["season_id"] = int(self.season_id)
        df_all_team_logs["date"] = self.date.strftime("%Y-%m-%d")
        logging.info("...Raw Team Stats DF Generated")
        df_all_team_logs = df_all_team_logs.dropna()
        return df_all_team_logs
