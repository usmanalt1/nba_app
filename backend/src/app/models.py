from django.db import models


class SeasonRecord(models.Model):
    season_id = models.IntegerField(unique=True)
    season = models.CharField(max_length=20, null=True, blank=True)
    run_timestamp = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'season_record'


class TeamInfo(models.Model):
    season_id = models.IntegerField()
    abbreviation = models.CharField(max_length=10)
    nickname = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    year_founded = models.IntegerField()
    full_name = models.CharField(max_length=100, null=True, blank=True)
    season = models.CharField(max_length=20, null=True, blank=True)
    run_timestamp = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'teams_info'
        constraints = [
            models.UniqueConstraint(fields=["season_id", "abbreviation"], name="teams_info_unique_season_abbr"),
        ]


class PlayerInfo(models.Model):
    season_id = models.IntegerField()
    full_name = models.CharField(max_length=100)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_active = models.BooleanField()
    season = models.CharField(max_length=20, null=True, blank=True)
    run_timestamp = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'players_info'
        constraints = [
            models.UniqueConstraint(fields=["season_id", "full_name"], name="players_info_unique_season_name"),
        ]


class TeamRoster(models.Model):
    team_id = models.IntegerField()
    player_id = models.IntegerField()
    season_id = models.IntegerField()
    player = models.CharField(max_length=100)
    age = models.IntegerField(null=True, blank=True)
    position = models.CharField(max_length=20, null=True, blank=True)
    season = models.CharField(max_length=20, null=True, blank=True)
    run_timestamp = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'teams_roster'
        constraints = [
            models.UniqueConstraint(fields=["team_id", "player_id", "season_id"], name="teams_roster_unique_team_player_season"),
        ]


class PlayerStats(models.Model):
    season_id = models.IntegerField()
    player_id = models.IntegerField()
    player_name = models.CharField(max_length=100)
    team_id = models.IntegerField()
    team_abbreviation = models.CharField(max_length=10)
    team_name = models.CharField(max_length=50)
    game_id = models.CharField(max_length=20)
    game_date = models.DateField(null=True, blank=True)
    matchup = models.CharField(max_length=50)
    wl = models.CharField(max_length=2, null=True, blank=True)
    min = models.FloatField()
    fgm = models.FloatField()
    fga = models.FloatField()
    fg_pct = models.FloatField()
    fg3m = models.FloatField()
    fg3a = models.FloatField()
    fg3_pct = models.FloatField()
    ftm = models.FloatField()
    fta = models.FloatField()
    ft_pct = models.FloatField()
    oreb = models.FloatField()
    dreb = models.FloatField()
    reb = models.FloatField()
    ast = models.FloatField()
    stl = models.FloatField()
    blk = models.FloatField()
    tov = models.FloatField()
    pf = models.FloatField()
    pts = models.FloatField()
    plus_minus = models.FloatField()
    fantasy_pts = models.FloatField(null=True, blank=True)
    video_available = models.IntegerField(null=True, blank=True)
    season = models.CharField(max_length=20, null=True, blank=True)
    run_timestamp = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'player_stats'
        constraints = [
            models.UniqueConstraint(fields=["game_id", "player_id", "season_id"], name="player_stats_unique_game_player_season"),
        ]


class TeamStats(models.Model):
    season_id = models.IntegerField()
    team_id = models.IntegerField()
    team_abbreviation = models.CharField(max_length=10)
    team_name = models.CharField(max_length=50)
    game_id = models.CharField(max_length=20)
    game_date = models.DateField(null=True, blank=True)
    matchup = models.CharField(max_length=50)
    wl = models.CharField(max_length=2, null=True, blank=True)
    min = models.FloatField()
    fgm = models.FloatField()
    fga = models.FloatField()
    fg_pct = models.FloatField()
    fg3m = models.FloatField()
    fg3a = models.FloatField()
    fg3_pct = models.FloatField()
    ftm = models.FloatField()
    fta = models.FloatField()
    ft_pct = models.FloatField()
    oreb = models.FloatField()
    dreb = models.FloatField()
    reb = models.FloatField()
    ast = models.FloatField()
    stl = models.FloatField()
    blk = models.FloatField()
    tov = models.FloatField()
    pf = models.FloatField()
    pts = models.FloatField()
    plus_minus = models.FloatField()
    video_available = models.IntegerField(null=True, blank=True)
    season = models.CharField(max_length=20, null=True, blank=True)
    run_timestamp = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'team_stats'
        constraints = [
            models.UniqueConstraint(fields=["game_id", "team_id", "season_id"], name="team_stats_unique_game_team_season"),
        ]


class TeamMatchups(models.Model):
    season_id = models.IntegerField()
    team_id = models.IntegerField()
    team_abbreviation = models.CharField(max_length=10)
    team_name = models.CharField(max_length=50)
    game_id = models.CharField(max_length=20)
    game_date = models.DateField(null=True, blank=True)
    matchup = models.CharField(max_length=50)
    wl = models.CharField(max_length=2, null=True, blank=True)
    min = models.FloatField()
    pts = models.FloatField()
    fgm = models.FloatField()
    fga = models.FloatField()
    fg_pct = models.FloatField()
    fg3m = models.FloatField()
    fg3a = models.FloatField()
    fg3_pct = models.FloatField()
    ftm = models.FloatField()
    fta = models.FloatField()
    ft_pct = models.FloatField()
    oreb = models.FloatField()
    dreb = models.FloatField()
    reb = models.FloatField()
    ast = models.FloatField()
    stl = models.FloatField()
    blk = models.FloatField()
    tov = models.FloatField()
    pf = models.FloatField()
    plus_minus = models.FloatField()
    season = models.CharField(max_length=20, null=True, blank=True)
    run_timestamp = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'team_matchups'
        constraints = [
            models.UniqueConstraint(fields=["season_id", "team_id", "game_date"], name="team_matchups_unique_season_team_date"),
        ]


class PlayerAwards(models.Model):
    player_id = models.IntegerField()
    first_name = models.TextField(null=True, blank=True)
    last_name = models.TextField(null=True, blank=True)
    team = models.TextField(null=True, blank=True)
    # the DESCRIPTION field is what actually distinguishes award types (e.g. "All-NBA",
    # "NBA All-Star", "NBA Most Valuable Player") - the API's own TYPE field is always "Award"
    description = models.TextField()
    all_nba_team_number = models.TextField(null=True, blank=True)
    season = models.TextField(null=True, blank=True)
    month = models.TextField(null=True, blank=True)
    week = models.TextField(null=True, blank=True)
    conference = models.TextField(null=True, blank=True)
    subtype1 = models.TextField(null=True, blank=True)
    subtype2 = models.TextField(null=True, blank=True)
    subtype3 = models.TextField(null=True, blank=True)
    run_timestamp = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'player_awards'
        constraints = [
            models.UniqueConstraint(
                fields=["player_id", "season", "description", "all_nba_team_number", "month", "week"],
                name="player_awards_unique_player_season_desc_month_week",
            ),
        ]


# ── Mart models (dbt-managed, read-only) ─────────────────────────────────────

class DimPlayers(models.Model):
    player_id = models.IntegerField(primary_key=True)
    season_id = models.CharField(max_length=20)
    player_name = models.CharField(max_length=100)
    age = models.IntegerField(null=True, blank=True)
    position = models.CharField(max_length=20, null=True, blank=True)
    first_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(null=True, blank=True)
    season = models.CharField(max_length=20, null=True, blank=True)
    run_timestamp = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = '"nba_marts"."dim_players"'


class DimGames(models.Model):
    game_id = models.CharField(max_length=20, primary_key=True)
    game_date = models.DateField(null=True, blank=True)
    season_id = models.IntegerField()
    season = models.CharField(max_length=20, null=True, blank=True)
    home_team_id = models.IntegerField()
    home_team_abbreviation = models.CharField(max_length=10)
    home_team_name = models.CharField(max_length=50)
    home_pts = models.FloatField(null=True, blank=True)
    home_wl = models.CharField(max_length=2, null=True, blank=True)
    away_team_id = models.IntegerField()
    away_team_abbreviation = models.CharField(max_length=10)
    away_team_name = models.CharField(max_length=50)
    away_pts = models.FloatField(null=True, blank=True)
    away_wl = models.CharField(max_length=2, null=True, blank=True)
    run_timestamp = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = '"nba_marts"."dim_games"'


class DimTeams(models.Model):
    team_id = models.IntegerField(primary_key=True)
    season_id = models.IntegerField()
    team_name = models.CharField(max_length=50)
    team_abbreviation = models.CharField(max_length=10)
    nickname = models.CharField(max_length=50, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    year_founded = models.IntegerField(null=True, blank=True)
    season = models.CharField(max_length=20, null=True, blank=True)
    run_timestamp = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = '"nba_marts"."dim_teams"'


class DimRosters(models.Model):
    player_id = models.IntegerField(primary_key=True)
    player_name = models.CharField(max_length=100)
    team_id = models.CharField(max_length=20)
    team_abbreviation = models.CharField(max_length=10)
    season_id = models.CharField(max_length=20)
    season = models.CharField(max_length=20)
    first_game_with_team = models.DateField(null=True, blank=True)
    last_game_with_team = models.DateField(null=True, blank=True)
    was_traded = models.BooleanField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = '"nba_marts"."dim_rosters"'


class DimSeasons(models.Model):
    season_id = models.IntegerField(primary_key=True)
    season_name = models.CharField(max_length=20, null=True, blank=True)
    run_timestamp = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = '"nba_marts"."dim_seasons"'


class FctPlayerStats(models.Model):
    season_id = models.CharField(max_length=20)
    player = models.ForeignKey(
        DimPlayers,
        on_delete=models.DO_NOTHING,
        db_column='player_id',
        db_constraint=False,
    )
    team_id = models.IntegerField()
    game_id = models.CharField(max_length=20, primary_key=True)
    wl = models.CharField(max_length=2, null=True, blank=True)
    min = models.FloatField(null=True, blank=True)
    fgm = models.FloatField(null=True, blank=True)
    fga = models.FloatField(null=True, blank=True)
    fg_pct = models.FloatField(null=True, blank=True)
    fg3m = models.FloatField(null=True, blank=True)
    fg3a = models.FloatField(null=True, blank=True)
    fg3_pct = models.FloatField(null=True, blank=True)
    ftm = models.FloatField(null=True, blank=True)
    fta = models.FloatField(null=True, blank=True)
    ft_pct = models.FloatField(null=True, blank=True)
    oreb = models.FloatField(null=True, blank=True)
    dreb = models.FloatField(null=True, blank=True)
    reb = models.FloatField(null=True, blank=True)
    ast = models.FloatField(null=True, blank=True)
    stl = models.FloatField(null=True, blank=True)
    blk = models.FloatField(null=True, blank=True)
    tov = models.FloatField(null=True, blank=True)
    pf = models.FloatField(null=True, blank=True)
    pts = models.FloatField(null=True, blank=True)
    plus_minus = models.FloatField(null=True, blank=True)
    season = models.CharField(max_length=20, null=True, blank=True)
    run_timestamp = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = '"nba_marts"."fct_player_stats"'


class FctTeamStats(models.Model):
    season_id = models.IntegerField()
    team_id = models.IntegerField()
    game_id = models.CharField(max_length=20, primary_key=True)
    wl = models.CharField(max_length=2, null=True, blank=True)
    min = models.FloatField(null=True, blank=True)
    fgm = models.FloatField(null=True, blank=True)
    fga = models.FloatField(null=True, blank=True)
    fg_pct = models.FloatField(null=True, blank=True)
    fg3m = models.FloatField(null=True, blank=True)
    fg3a = models.FloatField(null=True, blank=True)
    fg3_pct = models.FloatField(null=True, blank=True)
    ftm = models.FloatField(null=True, blank=True)
    fta = models.FloatField(null=True, blank=True)
    ft_pct = models.FloatField(null=True, blank=True)
    oreb = models.FloatField(null=True, blank=True)
    dreb = models.FloatField(null=True, blank=True)
    reb = models.FloatField(null=True, blank=True)
    ast = models.FloatField(null=True, blank=True)
    stl = models.FloatField(null=True, blank=True)
    blk = models.FloatField(null=True, blank=True)
    tov = models.FloatField(null=True, blank=True)
    pf = models.FloatField(null=True, blank=True)
    pts = models.FloatField(null=True, blank=True)
    plus_minus = models.FloatField(null=True, blank=True)
    season = models.CharField(max_length=20, null=True, blank=True)
    run_timestamp = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = '"nba_marts"."fct_team_stats"'


class MlModels(models.Model):
    model_name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'ml_models'