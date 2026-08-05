export type Metrics = { accuracy: number; log_loss: number; brier: number; auc: number };
export type SeasonRecord = { team: string; wins: number; loss: number; season: string };
export type Prediction = {
    game_id: string;
    game_date: string;
    matchup: string;
    home_win_probability: number;
    predicted_home_win: boolean;
    actual_home_win: boolean;
    home_team_name: string
};
export type TrainResponse = {
    success: boolean;
    error: string | null;
    metrics: Metrics | null;
    season_records: SeasonRecord[] | null;
    predictions: Prediction[] | null;
};
