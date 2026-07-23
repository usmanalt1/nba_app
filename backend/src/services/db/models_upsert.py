from logging import getLogger

logger = getLogger(__name__)

from app.models import PlayerInfo

class TableModel:
    def upsert(self, model, record):
        raise NotImplementedError

class SeasonRecord(TableModel):
    def upsert(self, model, record):
        model.objects.update_or_create(
            season_id=record["season_id"],
            defaults=record
        )
class TeamInfo(TableModel):
    def upsert(self, model, record):
        model.objects.update_or_create(
            season_id=record["season_id"],
            abbreviation=record["abbreviation"],
            defaults=record
        )
class TeamStats(TableModel):
    def upsert(self, model, record):
        model.objects.update_or_create(
            game_id=record["game_id"],
            team_id=record["team_id"],
            season_id=record["season_id"],
            defaults=record
        )
class PlayerStats(TableModel):
    def upsert(self, model, record):
        model.objects.update_or_create(
            game_id=record["game_id"],
            player_id=record["player_id"],
            season_id=record["season_id"],
            defaults=record
        )
class PlayersInfo(TableModel):
    def upsert(self, model: type[PlayerInfo], record):
        model.objects.update_or_create(
            season_id=record["season_id"],
            full_name=record["full_name"],
            defaults=record
        )

class TeamsRoster(TableModel):
    def upsert(self, model, record):
        model.objects.update_or_create(
            team_id=record["team_id"],
            player_id=record["player_id"],
            season_id=record["season_id"],
            defaults=record
        )
class TeamMatchups(TableModel):
    def upsert(self, model, record):
        model.objects.update_or_create(
            season_id=record["season_id"],
            team_id=record["team_id"],
            game_date=record["game_date"],
            defaults=record
        )

class PlayerAwards(TableModel):
    def upsert(self, model, record):
        # month/week are included since a player can hold the same award description
        # more than once in a season (e.g. multiple "NBA Player of the Month"); for
        # season-level awards these are None on every row, so they still collapse
        # to one row per (player, season, description) as expected.
        model.objects.update_or_create(
            player_id=record["player_id"],
            season=record["season"],
            description=record["description"],
            all_nba_team_number=record.get("all_nba_team_number"),
            month=record.get("month"),
            week=record.get("week"),
            defaults=record
        )


class TableModelFactory:
    @staticmethod
    def get_table_model(table: str) -> TableModel:
        table_model = {
            "season_record": SeasonRecord(),
            "teams_info": TeamInfo(),
            "team_stats": TeamStats(),
            "player_stats": PlayerStats(),
            "players_info": PlayersInfo(),
            "teams_roster": TeamsRoster(),
            "team_matchups": TeamMatchups(),
            "player_awards": PlayerAwards()
        }
        return table_model.get(table)