/** Per-game averages shared by the player and team stat endpoints. */
export interface BoxScoreAverages {
    games_played: number;
    average_minutes: number | null;
    average_points: number | null;
    average_field_goals_made: number | null;
    average_field_goals_attempted: number | null;
    field_goal_pct: number | null;
    average_three_pointers_made: number | null;
    average_three_pointers_attempted: number | null;
    three_point_pct: number | null;
    average_free_throws_made: number | null;
    average_free_throws_attempted: number | null;
    free_throw_pct: number | null;
    average_offensive_rebounds: number | null;
    average_defensive_rebounds: number | null;
    average_rebounds: number | null;
    average_assists: number | null;
    average_steals: number | null;
    average_blocks: number | null;
    average_turnovers: number | null;
    average_fouls: number | null;
    average_plus_minus: number | null;
}

/** Season-level advanced metrics. Shares are already 0-100 from the API. */
export interface AdvancedAverages {
    games_played: number | null;
    wins: number | null;
    losses: number | null;
    average_minutes: number | null;
    offensive_rating: number | null;
    defensive_rating: number | null;
    net_rating: number | null;
    true_shooting_percentage: number | null;
    effective_field_goal_percentage: number | null;
    usage_percentage: number | null;
    assist_percentage: number | null;
    assist_to_turnover: number | null;
    assist_ratio: number | null;
    turnover_percentage: number | null;
    offensive_rebound_percentage: number | null;
    defensive_rebound_percentage: number | null;
    rebound_percentage: number | null;
    pace: number | null;
    possessions: number | null;
    pie: number | null;
}

export interface SeasonAdvancedPlayerStats extends AdvancedAverages {
    player_id: number;
    player_name: string | null;
    season: string;
    position: string | null;
    team_abbreviation: string | null;
    age: number | null;
}

export interface SeasonAdvancedTeamStats extends AdvancedAverages {
    team_id: number;
    team_name: string | null;
    season: string;
}
