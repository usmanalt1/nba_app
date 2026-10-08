export type Metrics = { accuracy: number; log_loss: number; brier: number; auc: number };
export type SeasonRecord = { team: string; wins: number; loss: number; season: string };
export type Prediction = {
    game_id: string;
    game_date: string;
    matchup: string;
    home_win_probability: number;
    predicted_home_win: boolean;
    // null until played - gradePredictions drops these rather than scoring a miss
    actual_home_win: boolean | null;
    home_team_name: string;
    away_team_name?: string | null;
    season?: string;
    season_type?: string;
};
export type TrainResponse = {
    success: boolean;
    error: string | null;
    metrics: Metrics | null;
    season_records: SeasonRecord[] | null;
    predictions: Prediction[] | null;
};
export type ModelRunSummary = { strategy: string; season: string; season_type: string; metrics: Metrics };
