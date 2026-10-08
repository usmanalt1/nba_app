from logging import getLogger

import pandas as pd

logger = getLogger(__name__)

class TableModel:
    unique_fields: list = []
    # Column to receive the source's own "id", for tables whose entity id the marts join
    # on (teams_info, players_info). Dropping it there produced fictional teams in
    # dim_teams; it cannot stay as `id` because that is the pk and must not repeat.
    source_id_field: str = None

    def upsert_many(self, model, records: list) -> None:
        if not records:
            return
        if not self.unique_fields:
            raise NotImplementedError(f"{type(self).__name__} has no unique_fields to upsert on")

        # source "id" is never Django's pk - carried to a named column or dropped
        records = [
            {
                **({self.source_id_field: record["id"]}
                   if self.source_id_field and "id" in record else {}),
                **{k: v for k, v in record.items() if k != "id"},
            }
            for record in records
        ]

        # Postgres' ON CONFLICT can't apply two updates to the same row within one
        # statement, so a batch with two records sharing the same unique_fields raises
        # "cannot affect row a second time" - keep the last occurrence of each key.
        # NOTE: this is a safety net, not a fix for the underlying cause - if this fires,
        # it usually means the upstream collector produced genuinely duplicate/mislabeled
        # rows (seen with teams_info/players_info tagging multiple seasons identically).
        before = len(records)
        deduped = {tuple(record[f] for f in self.unique_fields): record for record in records}
        records = list(deduped.values())
        if len(records) < before:
            logger.warning(f"Dropped {before - len(records)} duplicate records on {self.unique_fields} before upsert")

        update_fields = [f for f in records[0].keys() if f not in self.unique_fields]
        instances = [model(**record) for record in records]
        model.objects.bulk_create(
            instances,
            update_conflicts=True,
            unique_fields=self.unique_fields,
            update_fields=update_fields,
            batch_size=1000,
        )

    def read(self, model) -> list:
        return list(model.objects.all().values())

class SeasonRecord(TableModel):
    unique_fields = ["season_id"]

class TeamInfo(TableModel):
    unique_fields = ["season_id", "abbreviation"]
    source_id_field = "team_id"

class TeamStats(TableModel):
    unique_fields = ["game_id", "team_id", "season_id"]

class PlayerStats(TableModel):
    unique_fields = ["game_id", "player_id", "season_id"]

class PlayersInfo(TableModel):
    unique_fields = ["season_id", "full_name"]
    source_id_field = "player_id"

class TeamsRoster(TableModel):
    unique_fields = ["team_id", "player_id", "season_id"]

class TeamMatchups(TableModel):
    unique_fields = ["season_id", "team_id", "game_date"]

class GameSchedule(TableModel):
    unique_fields = ["game_id"]

class PlayerAwards(TableModel):
    # month/week are included since a player can hold the same award description
    # more than once in a season (e.g. multiple "NBA Player of the Month"); for
    # season-level awards these are None on every row, so they still collapse
    # to one row per (player, season, description) as expected.
    unique_fields = ["player_id", "season", "description", "all_nba_team_number", "month", "week"]

class AdvancedPlayerSeasonStats(TableModel):
    unique_fields = ["season", "season_type", "player_id"]

class AdvancedTeamSeasonStats(TableModel):
    unique_fields = ["season", "season_type", "team_id"]

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
            "player_awards": PlayerAwards(),
            "game_schedule": GameSchedule(),
            "advanced_player_season_stats": AdvancedPlayerSeasonStats(),
            "advanced_team_season_stats": AdvancedTeamSeasonStats(),
            "dim_games": TableModel(),
            "fct_team_stats": TableModel(),
            "fct_player_stats": TableModel(),
            "dim_rosters": TableModel(),
            "dim_teams": TableModel(),
        }
        return table_model.get(table)
