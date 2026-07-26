from logging import getLogger

import pandas as pd

logger = getLogger(__name__)

class TableModel:
    unique_fields: list = []

    def upsert_many(self, model, records: list) -> None:
        if not records:
            return
        if not self.unique_fields:
            raise NotImplementedError(f"{type(self).__name__} has no unique_fields to upsert on")

        # some raw sources (e.g. teams_info/players_info) carry their own "id" column
        # from the NBA API - that's unrelated to Django's auto-assigned primary key and
        # must never be set from incoming data, so strip it before building instances
        records = [{k: v for k, v in record.items() if k != "id"} for record in records]

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

class TeamStats(TableModel):
    unique_fields = ["game_id", "team_id", "season_id"]

class PlayerStats(TableModel):
    unique_fields = ["game_id", "player_id", "season_id"]

class PlayersInfo(TableModel):
    unique_fields = ["season_id", "full_name"]

class TeamsRoster(TableModel):
    unique_fields = ["team_id", "player_id", "season_id"]

class TeamMatchups(TableModel):
    unique_fields = ["season_id", "team_id", "game_date"]

class PlayerAwards(TableModel):
    # month/week are included since a player can hold the same award description
    # more than once in a season (e.g. multiple "NBA Player of the Month"); for
    # season-level awards these are None on every row, so they still collapse
    # to one row per (player, season, description) as expected.
    unique_fields = ["player_id", "season", "description", "all_nba_team_number", "month", "week"]

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
            "dim_games": TableModel(),
            "fct_team_stats": TableModel(),
            "fct_player_stats": TableModel(),
        }
        return table_model.get(table)
