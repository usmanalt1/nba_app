from logging import getLogger

logger = getLogger(__name__)

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
            date=record["date"],
            team_id=record["team_id"],
            season_year=record["season_year"],
            defaults=record
        )
class PlayerStats(TableModel):
    def upsert(self, model, record):
        model.objects.update_or_create(
            date=record["date"],
            player_id=record["player_id"],
            season_id=record["season_id"],
            defaults=record
        )
class PlayersInfo(TableModel):
    def upsert(self, model, record):
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


class TableModelFactory:
    @staticmethod
    def get_table_model(table: str) -> TableModel:
        table_model = {
            "season_record": SeasonRecord(),
            "team_info": TeamInfo(),
            "team_stats": TeamStats(),
            "player_stats": PlayerStats(),
            "players_info": PlayersInfo(),
            "teams_roster": TeamsRoster(),
            "team_matchups": TeamMatchups()
        }
        return table_model.get(table)