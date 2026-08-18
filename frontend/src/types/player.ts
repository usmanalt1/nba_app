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

export interface RankedPlayerStats {
    season_id: string
    season: string
    player_id: string
    team_id: string
    average_points: number
    average_rebounds: number
    average_plus_minus: number
    average_assists: number
    average_defensive_rebounds: number
    average_offensive_rebounds: number
    games_played: number
    player_name: string
    team_name: string
    rank_average_points: number
    rank_average_rebounds: number
    rank_average_plus_minus: number
    rank_average_assists: number
    rank_average_defensive_rebounds: number
    rank_average_offensive_rebounds: number
}