export interface MostImprovedPlayer {
    season_id: string
    player_id: number
    team_id: number
    season: string
    current_average_points: number
    games_played: number
    player_name: string
    team_name: string
    previous_average_points: number
    games_played_previous: number
    points_improvement: number
}

export interface MostImprovedTeam {
    season_id: string
    team_id: number
    season: string
    wins: number
    games_played: number
    current_win_pct: number
    team_name: string
    previous_win_pct: number
    games_played_previous: number
    win_pct_improvement: number
}
