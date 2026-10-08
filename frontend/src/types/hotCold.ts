export interface HotColdRow {
    scope: 'player' | 'team';
    entity_id: number;
    name: string;
    team_id: number;
    games: number;
    /** Last 10 games: points per game for players, average margin for teams. */
    form: number;
    /** The same measure over every earlier game, excluding those 10. */
    baseline: number;
    delta: number;
    form_ts_pct?: number | null;
    delta_ts_pct?: number | null;
    form_wins?: number | null;
    form_games?: number | null;
    delta_win_pct?: number | null;
}

export interface HotColdResponse {
    success: boolean;
    error?: string | null;
    records?: HotColdRow[] | null;
    /** The season served, or null when none has enough games yet. */
    season?: string | null;
    latest_season?: string | null;
    season_is_fallback: boolean;
    min_games: number;
}
