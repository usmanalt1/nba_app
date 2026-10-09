import { useEffect, useState } from 'react';
import { SectionHeader } from '../ui/SectionHeader';
import { Leaderboard, type LeaderboardRow } from '../ui/Leaderboard';
import { apiFetch } from '../../lib/api';
import { useStatsSeason } from '../../hooks/useStatsSeason';
import type { RankedPlayerStats } from '../../types/player';
import type { RankedTeamStats } from '../../types/team';

/** A first-round exit is four games, so this keeps a rank off a single hot night. */
const MIN_PLAYOFF_GAMES = 5;
const SHOWN = 5;

interface HomePostseasonProps {
    index: string;
}

// The last completed postseason, not the live season: most of the year has no playoff.
export function HomePostseason({ index }: HomePostseasonProps) {
    const season = useStatsSeason('playoffs');
    const [players, setPlayers] = useState<RankedPlayerStats[]>([]);
    const [teams, setTeams] = useState<RankedTeamStats[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!season) return;
        let cancelled = false;
        const query = `season=${season}/season_type=playoffs?min_games=${MIN_PLAYOFF_GAMES}`;

        Promise.all([
            apiFetch(`/api/nba/analytics/average_stats/${query}`).then(r => r.json()),
            apiFetch(`/api/nba/analytics/average_team_stats/${query}`).then(r => r.json()),
        ])
            .then(([playerData, teamData]) => {
                if (cancelled) return;
                setPlayers(playerData.records ?? []);
                setTeams(teamData.records ?? []);
                setLoading(false);
            })
            .catch(() => { if (!cancelled) setLoading(false); });

        return () => { cancelled = true; };
    }, [season]);

    const scoringRows: LeaderboardRow[] = [...players]
        .sort((a, b) => b.average_points - a.average_points)
        .slice(0, SHOWN)
        .map((player, index) => ({
            rank: index + 1,
            label: player.player_name,
            sublabel: `${player.team_name} · ${player.games_played} games`,
            value: player.average_points.toFixed(1),
            magnitude: player.average_points,
        }));

    const marginRows: LeaderboardRow[] = [...teams]
        .sort((a, b) => b.average_plus_minus - a.average_plus_minus)
        .slice(0, SHOWN)
        .map((team, index) => ({
            rank: index + 1,
            label: team.team_name,
            sublabel: `${team.wins}-${team.games_played - team.wins} · ${team.average_points.toFixed(1)} ppg`,
            value: `${team.average_plus_minus > 0 ? '+' : ''}${team.average_plus_minus.toFixed(1)}`,
            magnitude: team.average_plus_minus,
        }));

    return (
        <section style={{ marginBottom: 'var(--section-gap)' }}>
            <SectionHeader
                index={index}
                title="Last Postseason"
                subtitle={
                    season
                        ? `Who carried the ${season} playoffs, once the games got heavier`
                        : 'Who carried the last playoffs'
                }
                meta={
                    season && (
                        <span className="kicker" style={{ color: 'var(--paper-faint)' }}>
                            {season} · min {MIN_PLAYOFF_GAMES} games
                        </span>
                    )
                }
            />

            {!season || loading ? (
                <div style={{ fontSize: 13, color: 'var(--paper-faint)', padding: '8px 0' }}>
                    {season ? 'Reading the postseason…' : 'No postseason on record yet.'}
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 20 }}>
                    <Leaderboard
                        accent
                        title="Playoff Scoring"
                        titleMeta="per game"
                        rows={scoringRows}
                        empty="No qualifying scorers."
                    />
                    <Leaderboard
                        title="Playoff Margin"
                        titleMeta="per game"
                        rows={marginRows}
                        empty="No qualifying teams."
                    />
                </div>
            )}
        </section>
    );
}
