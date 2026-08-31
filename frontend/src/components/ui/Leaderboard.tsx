import { Panel } from './Panel';

export interface LeaderboardRow {
    rank: number;
    label: string;
    sublabel?: string;
    value: string | number;
}

interface LeaderboardProps {
    title: string;
    unit?: string;
    rows: LeaderboardRow[];
}

export function Leaderboard({ title, unit = '', rows }: LeaderboardProps) {
    return (
        <Panel title={title} style={{ width: '100%' }}>
            <div>
                {rows.map((row, index) => {
                    const isLeader = row.rank === 1;
                    return (
                        <div
                            key={`${row.rank}-${row.label}`}
                            style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: 12,
                                padding: '6px 0',
                                borderBottom: index === rows.length - 1 ? 'none' : '1px solid var(--line)',
                                fontFamily: "'IBM Plex Mono', monospace",
                            }}
                        >
                            <span
                                style={{
                                    width: 20,
                                    flexShrink: 0,
                                    fontSize: 13,
                                    fontWeight: 700,
                                    color: isLeader ? 'var(--gold)' : 'var(--paper-dim)',
                                }}
                            >
                                {row.rank}
                            </span>
                            <div style={{ flex: 1, minWidth: 0 }}>
                                <div
                                    style={{
                                        fontWeight: isLeader ? 600 : 400,
                                        color: isLeader ? 'var(--gold)' : 'var(--paper)',
                                        fontSize: 14,
                                        whiteSpace: 'nowrap',
                                        overflow: 'hidden',
                                        textOverflow: 'ellipsis',
                                    }}
                                >
                                    {row.label}
                                </div>
                                {row.sublabel && (
                                    <div style={{ fontSize: 11, color: 'var(--paper-dim)' }}>{row.sublabel}</div>
                                )}
                            </div>
                            <div
                                style={{
                                    flexShrink: 0,
                                    fontWeight: 700,
                                    fontSize: 14,
                                    color: isLeader ? 'var(--gold)' : 'var(--paper)',
                                }}
                            >
                                {row.value}{unit}
                            </div>
                        </div>
                    );
                })}
            </div>
        </Panel>
    );
}
