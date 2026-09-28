import { Panel } from './Panel';

export interface LeaderboardRow {
    rank: number;
    label: string;
    sublabel?: string;
    value: string | number;
    /** Drives the magnitude track behind the row. Falls back to a plain list when absent. */
    magnitude?: number;
}

interface LeaderboardProps {
    title: string;
    titleMeta?: string;
    unit?: string;
    rows: LeaderboardRow[];
    /** Marks this board as the section's lead. */
    accent?: boolean;
    empty?: string;
}

export function Leaderboard({ title, titleMeta, unit = '', rows, accent, empty = 'No data yet.' }: LeaderboardProps) {
    const peak = Math.max(...rows.map((row) => row.magnitude ?? 0), 0);

    return (
        <Panel title={title} titleMeta={titleMeta} accent={accent} style={{ width: '100%' }}>
            {rows.length === 0 ? (
                <div style={{ fontSize: 13, color: 'var(--paper-faint)' }}>{empty}</div>
            ) : (
                rows.map((row, index) => {
                    const isLeader = index === 0;
                    // Zero-based: a floor would exaggerate gaps between players who are
                    // in reality a tenth of a rebound apart.
                    const fill = peak > 0 && row.magnitude !== undefined
                        ? (row.magnitude / peak) * 100
                        : null;

                    return (
                        <div
                            key={`${row.rank}-${row.label}`}
                            style={{
                                position: 'relative',
                                display: 'flex',
                                alignItems: 'center',
                                gap: 12,
                                padding: '7px 8px 7px 0',
                                borderBottom: index === rows.length - 1 ? 'none' : '1px solid var(--line)',
                                fontFamily: 'var(--mono)',
                            }}
                        >
                            {fill !== null && (
                                <span
                                    aria-hidden
                                    style={{
                                        position: 'absolute',
                                        left: -18,
                                        top: 2,
                                        bottom: 2,
                                        width: `calc(${fill}% + 18px)`,
                                        background: isLeader ? 'rgba(232, 98, 44, 0.14)' : 'rgba(232, 98, 44, 0.05)',
                                        borderRight: isLeader ? '2px solid var(--worm)' : 'none',
                                        pointerEvents: 'none',
                                    }}
                                />
                            )}

                            <span
                                style={{
                                    position: 'relative',
                                    width: 18,
                                    flexShrink: 0,
                                    fontSize: 12,
                                    fontWeight: 700,
                                    color: isLeader ? 'var(--worm)' : 'var(--paper-faint)',
                                    fontVariantNumeric: 'tabular-nums',
                                }}
                            >
                                {row.rank}
                            </span>

                            <div style={{ position: 'relative', flex: 1, minWidth: 0 }}>
                                <div
                                    style={{
                                        fontWeight: isLeader ? 600 : 400,
                                        color: 'var(--paper)',
                                        fontSize: 13,
                                        whiteSpace: 'nowrap',
                                        overflow: 'hidden',
                                        textOverflow: 'ellipsis',
                                    }}
                                    title={row.label}
                                >
                                    {row.label}
                                </div>
                                {row.sublabel && (
                                    <div
                                        style={{
                                            fontSize: 11,
                                            color: 'var(--paper-dim)',
                                            whiteSpace: 'nowrap',
                                            overflow: 'hidden',
                                            textOverflow: 'ellipsis',
                                        }}
                                        title={row.sublabel}
                                    >
                                        {row.sublabel}
                                    </div>
                                )}
                            </div>

                            <div
                                style={{
                                    position: 'relative',
                                    flexShrink: 0,
                                    fontWeight: 700,
                                    fontSize: 13,
                                    color: isLeader ? 'var(--worm)' : 'var(--paper)',
                                    fontVariantNumeric: 'tabular-nums',
                                }}
                            >
                                {row.value}{unit}
                            </div>
                        </div>
                    );
                })
            )}
        </Panel>
    );
}
