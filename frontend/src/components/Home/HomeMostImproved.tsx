import { useEffect, useState } from "react";
import type { MostImprovedPlayer, MostImprovedTeam } from '../../types/mostImproved';
import { Leaderboard, type LeaderboardRow } from '../ui/Leaderboard';
import { apiFetch } from '../../lib/api';
import { env } from '../../env';

export function HomeMostImproved() {
    const [players, setPlayers] = useState<MostImprovedPlayer[]>([]);
    const [teams, setTeams] = useState<MostImprovedTeam[]>([]);

    // These endpoints take season_type only: the comparison needs both the current
    // and previous season, so there is no season segment in the path.
    const seasonType = env.VITE_DEFAULT_SEASON_TYPE;

    useEffect(() => {
        apiFetch(`/api/nba/analytics/most_improved_players/season_type=${seasonType}`)
            .then(r => r.json())
            .then(data => setPlayers(data.records ?? []))
            .catch(() => setPlayers([]));
    }, [seasonType]);

    useEffect(() => {
        apiFetch(`/api/nba/analytics/most_improved_teams/season_type=${seasonType}`)
            .then(r => r.json())
            .then(data => setTeams(data.records ?? []))
            .catch(() => setTeams([]));
    }, [seasonType]);

    const playerRows: LeaderboardRow[] = players.slice(0, 10).map((player, index) => ({
        rank: index + 1,
        label: player.player_name,
        sublabel: `${player.team_name} · ${player.previous_average_points.toFixed(1)} → ${player.current_average_points.toFixed(1)} ppg`,
        value: `+${player.points_improvement.toFixed(1)}`,
        magnitude: player.points_improvement,
    }));

    const teamRows: LeaderboardRow[] = teams.slice(0, 10).map((team, index) => ({
        rank: index + 1,
        label: team.team_name,
        sublabel: `${(team.previous_win_pct * 100).toFixed(0)}% → ${(team.current_win_pct * 100).toFixed(0)}% win rate`,
        value: `+${(team.win_pct_improvement * 100).toFixed(1)}%`,
        magnitude: team.win_pct_improvement,
    }));

    return (
        <div style={{ width: '100%', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 20 }}>
            <Leaderboard
                accent
                title="Players — points gained"
                titleMeta="vs last season"
                rows={playerRows}
            />
            <Leaderboard
                title="Teams — win rate gained"
                titleMeta="vs last season"
                rows={teamRows}
            />
        </div>
    );
}
