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
