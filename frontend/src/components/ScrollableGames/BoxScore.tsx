import { useEffect, useState } from 'react';
import { Modal } from '@mantine/core';
import { apiFetch } from '../../lib/api';

export interface BoxScoreLine {
    player_id: number;
    player_name: string | null;
    team_id: number;
    min: number | null;
    pts: number | null;
    reb: number | null;
    ast: number | null;
    stl: number | null;
    blk: number | null;
    tov: number | null;
    fgm: number | null;
    fga: number | null;
    fg3m: number | null;
    fg3a: number | null;
    ftm: number | null;
    fta: number | null;
    plus_minus: number | null;
}

interface GameBoxScore {
    game_id: string;
    game_date: string | null;
    home_team_id: number;
    home_team_name: string | null;
    home_pts: number | null;
    away_team_id: number;
    away_team_name: string | null;
    away_pts: number | null;
    lines: BoxScoreLine[];
}

const num = (v: number | null) => (v === null || v === undefined ? '—' : String(Math.round(v)));
const signed = (v: number | null) => (v === null || v === undefined ? '—' : `${v > 0 ? '+' : ''}${Math.round(v)}`);

const cell: React.CSSProperties = {
    padding: '6px 8px',
    fontFamily: 'var(--mono)',
    fontSize: 12,
    textAlign: 'right',
    fontVariantNumeric: 'tabular-nums',
    color: 'var(--paper-dim)',
};

const headCell: React.CSSProperties = { ...cell, color: 'var(--paper-faint)', fontSize: 11 };

function TeamTable({ title, points, lines }: { title: string; points: number | null; lines: BoxScoreLine[] }) {
    if (lines.length === 0) return null;

    return (
        <div style={{ marginBottom: 26 }}>
            <div
                style={{
                    display: 'flex', justifyContent: 'space-between', alignItems: 'baseline',
                    marginBottom: 8, paddingBottom: 6, borderBottom: '1px solid var(--line)',
                }}
            >
                <span style={{ fontWeight: 700, color: 'var(--paper)' }}>{title}</span>
                <span style={{ fontFamily: 'var(--mono)', color: 'var(--paper)' }}>{num(points)}</span>
            </div>
            <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: 520 }}>
                    <thead>
                        <tr>
                            <th style={{ ...headCell, textAlign: 'left' }}>Player</th>
                            {['MIN', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TO', 'FG', '3P', 'FT', '+/-'].map(h => (
                                <th key={h} style={headCell}>{h}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {lines.map(line => (
                            <tr key={line.player_id}>
                                <td style={{ ...cell, textAlign: 'left', color: 'var(--paper)', whiteSpace: 'nowrap' }}>
                                    {line.player_name ?? '—'}
                                </td>
                                <td style={cell}>{num(line.min)}</td>
                                <td style={{ ...cell, color: 'var(--paper)', fontWeight: 600 }}>{num(line.pts)}</td>
                                <td style={cell}>{num(line.reb)}</td>
                                <td style={cell}>{num(line.ast)}</td>
                                <td style={cell}>{num(line.stl)}</td>
                                <td style={cell}>{num(line.blk)}</td>
                                <td style={cell}>{num(line.tov)}</td>
                                <td style={cell}>{num(line.fgm)}/{num(line.fga)}</td>
                                <td style={cell}>{num(line.fg3m)}/{num(line.fg3a)}</td>
                                <td style={cell}>{num(line.ftm)}/{num(line.fta)}</td>
                                <td style={cell}>{signed(line.plus_minus)}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}

export function BoxScore({ gameId, onClose }: { gameId: string | null; onClose: () => void }) {
    const [game, setGame] = useState<GameBoxScore | null>(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!gameId) return;

        let cancelled = false;
        setLoading(true);
        setGame(null);
        apiFetch(`/api/nba/db/game/${gameId}/box_score`)
            .then(r => r.json())
            .then(data => { if (!cancelled) setGame(data); })
            .catch(() => { if (!cancelled) setGame(null); })
            .finally(() => { if (!cancelled) setLoading(false); });

        return () => { cancelled = true; };
    }, [gameId]);

    const date = game?.game_date
        ? new Date(game.game_date).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })
        : '';

    return (
        <Modal
            opened={gameId !== null}
            onClose={onClose}
            size="xl"
            title={game ? `${game.away_team_name} ${num(game.away_pts)} @ ${game.home_team_name} ${num(game.home_pts)} · ${date}` : 'Box score'}
            styles={{ title: { fontWeight: 700 } }}
        >
            {loading && <div style={{ color: 'var(--paper-faint)', fontSize: 13 }}>Loading box score…</div>}
            {!loading && !game && <div style={{ color: 'var(--paper-faint)', fontSize: 13 }}>No box score for this game.</div>}
            {game && (
                <>
                    <TeamTable
                        title={game.away_team_name ?? 'Away'}
                        points={game.away_pts}
                        lines={game.lines.filter(l => l.team_id === game.away_team_id)}
                    />
                    <TeamTable
                        title={game.home_team_name ?? 'Home'}
                        points={game.home_pts}
                        lines={game.lines.filter(l => l.team_id === game.home_team_id)}
                    />
                </>
            )}
        </Modal>
    );
}
