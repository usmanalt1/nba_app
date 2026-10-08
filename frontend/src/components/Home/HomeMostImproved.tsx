import { useEffect, useState } from "react";
import type { MostImprovedPlayer, MostImprovedTeam } from '../../types/mostImproved';
import { Leaderboard, type LeaderboardRow } from '../ui/Leaderboard';
import { apiFetch } from '../../lib/api';

/** Both sides of the comparison need 20 games, which no postseason run reaches. */
const SUPPORTED_SEASON_TYPES = ['regular'];

export function HomeMostImproved({ seasonType = 'regular' }: { seasonType?: string } = {}) {
    const [players, setPlayers] = useState<MostImprovedPlayer[]>([]);
    const [teams, setTeams] = useState<MostImprovedTeam[]>([]);

    const supported = SUPPORTED_SEASON_TYPES.includes(seasonType);

    useEffect(() => {
        if (!supported) return;
        apiFetch(`/api/nba/analytics/most_improved_players/season_type=${seasonType}`)
            .then(r => r.json())
            .then(data => setPlayers(data.records ?? []))
            .catch(() => setPlayers([]));
    }, [seasonType, supported]);

    useEffect(() => {
        if (!supported) return;
        apiFetch(`/api/nba/analytics/most_improved_teams/season_type=${seasonType}`)
            .then(r => r.json())
            .then(data => setTeams(data.records ?? []))
            .catch(() => setTeams([]));
    }, [seasonType, supported]);

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

    if (!supported) {
        return (
            <div style={{ fontSize: 13, color: 'var(--paper-faint)', padding: '8px 0' }}>
                Regular season only — the comparison needs 20 games either side, and a
                postseason run never gets there.
            </div>
        );
    }

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
