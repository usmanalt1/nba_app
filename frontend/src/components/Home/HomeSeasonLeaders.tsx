import { useMemo } from 'react';
import { SectionHeader } from '../ui/SectionHeader';
import { Leaderboard, type LeaderboardRow } from '../ui/Leaderboard';
import { useSeasonPlayerStats, useSeasonTeamStats } from '../../hooks/useSeasonStats';
import type { SeasonPlayerStats } from '../../types/player';

/**
 * A player has to have played a real share of the season to hold a rank. Without this
 * the plus/minus board is won by whoever had one good night off the bench - a single
 * 7-minute appearance outranked every starter in 2025-26.
 */
const QUALIFY_GAME_SHARE = 0.4;
const QUALIFY_MINUTES = 20;

const SHOWN = 10;
/** Every board caps its body here and scrolls, so all five sit level in the row. */
const BOARD_HEIGHT = 292;

type StatKey = 'average_points' | 'average_assists' | 'average_rebounds' | 'average_plus_minus';

const STATS: { key: StatKey; title: string; signed?: boolean }[] = [
    { key: 'average_points', title: 'Points' },
    { key: 'average_assists', title: 'Assists' },
    { key: 'average_rebounds', title: 'Rebounds' },
    { key: 'average_plus_minus', title: 'Plus / Minus', signed: true },
];

function qualified(players: SeasonPlayerStats[]): SeasonPlayerStats[] {
    const busiest = players.reduce((most, player) => Math.max(most, player.games_played ?? 0), 0);
    const minGames = Math.max(1, Math.round(busiest * QUALIFY_GAME_SHARE));

    return players.filter((player) =>
        (player.games_played ?? 0) >= minGames && (player.average_minutes ?? 0) >= QUALIFY_MINUTES
    );
}

interface HomeSeasonLeadersProps {
    index: string;
    /** null while the caller resolves it, which holds the fetch */
    season?: string | null;
}

export function HomeSeasonLeaders({ index, season = null }: HomeSeasonLeadersProps) {
    const { rows: players, loading: loadingPlayers } = useSeasonPlayerStats(season);
    const { rows: teams, loading: loadingTeams } = useSeasonTeamStats(season);

    const boards = useMemo(() => {
        const pool = qualified(players);
        return STATS.map(({ key, title, signed }) => ({
            title,
            rows: [...pool]
                .sort((a, b) => (b[key] ?? 0) - (a[key] ?? 0))
                .slice(0, SHOWN)
                .map((player, position): LeaderboardRow => {
                    const value = player[key] ?? 0;
                    return {
                        rank: position + 1,
                        label: player.player_name,
                        sublabel: `${player.games_played} games`,
                        value: signed && value > 0 ? `+${value.toFixed(1)}` : value.toFixed(1),
                        magnitude: value,
                    };
                }),
        }));
    }, [players]);

    // Already ordered by wins by the endpoint.
    const teamRows: LeaderboardRow[] = teams.slice(0, SHOWN).map((team, position) => ({
        rank: position + 1,
        label: team.team_name,
        sublabel: `${((team.wins / Math.max(1, team.wins + team.losses)) * 100).toFixed(0)}% win rate`,
        value: `${team.wins}-${team.losses}`,
        magnitude: team.wins,
    }));

    const loading = loadingPlayers || loadingTeams;

    return (
        <section style={{ marginBottom: 'var(--section-gap)' }}>
            <SectionHeader
                index={index}
                title="Top of the Season"
                subtitle="Who leads the league as it stands, and who is winning most"
                meta={
                    season && (
                        <span className="kicker" style={{ color: 'var(--paper-faint)' }}>
                            {season} · {QUALIFY_MINUTES}+ mpg
                        </span>
                    )
                }
            />

            {loading ? (
                <div style={{ fontSize: 13, color: 'var(--paper-faint)', padding: '8px 0' }}>
                    Counting up the season…
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 20 }}>
                    {boards.map((board, position) => (
                        <Leaderboard
                            key={board.title}
                            accent={position === 0}
                            title={board.title}
                            titleMeta="per game"
                            rows={board.rows}
                            maxHeight={BOARD_HEIGHT}
                            empty="Nobody qualifies yet."
                        />
                    ))}
                    <Leaderboard
                        title="Best Records"
                        titleMeta="W-L"
                        rows={teamRows}
                        maxHeight={BOARD_HEIGHT}
                        empty="No games played yet."
                    />
                </div>
            )}
        </section>
    );
}
