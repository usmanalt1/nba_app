import { useEffect, useState } from "react";
import type { MostImprovedPlayer, MostImprovedTeam } from '../../types/mostImproved';
import { Leaderboard, type LeaderboardRow } from '../ui/Leaderboard';
import { apiFetch } from '../../lib/api';

export function HomeMostImproved() {
    const [players, setPlayers] = useState<MostImprovedPlayer[]>([]);
    const [teams, setTeams] = useState<MostImprovedTeam[]>([]);

    useEffect(() => {
        apiFetch("/api/nba/analytics/most_improved_players")
            .then(r => r.json())
            .then(data => setPlayers(data.records ?? []));
    }, []);

    useEffect(() => {
        apiFetch("/api/nba/analytics/most_improved_teams")
            .then(r => r.json())
            .then(data => setTeams(data.records ?? []));
    }, []);

    const playerRows: LeaderboardRow[] = players.map((player, index) => ({
        rank: index + 1,
        label: player.player_name,
        sublabel: `${player.team_name} — ${player.previous_average_points.toFixed(1)} → ${player.current_average_points.toFixed(1)} ppg`,
        value: `+${player.points_improvement.toFixed(1)}`,
    }));

    const teamRows: LeaderboardRow[] = teams.map((team, index) => ({
        rank: index + 1,
        label: team.team_name,
        sublabel: `${(team.previous_win_pct * 100).toFixed(0)}% → ${(team.current_win_pct * 100).toFixed(0)}% win rate`,
        value: `+${(team.win_pct_improvement * 100).toFixed(1)}%`,
    }));

    return (
        <div style={{ marginBottom: '30px', width: '100%', display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: '30px' }}>
            <Leaderboard title="Most Improved Players (PPG)" rows={playerRows} />
            <Leaderboard title="Most Improved Teams (Win %)" rows={teamRows} />
        </div>
    );
}
