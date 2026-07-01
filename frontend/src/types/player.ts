export interface RawPlayerStats {
    season_id: string;
    average_points: number;
    average_rebounds: number;
    average_plus_minus: number;
    average_assists: number;
}

export interface PlayerStats {
    season: string;
    points: number;
    rebounds: number;
    plusMinus: number;
    assists: number;
}
