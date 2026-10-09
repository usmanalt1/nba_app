import { useState } from 'react';
import { TeamChip } from './TeamChip';
import { diverging, divergingColour } from '../../lib/colour';
import type { TeamKey } from '../../context/TeamColoursProvider';

export interface DivergingRow {
    id: string | number;
    label: string;
    teamKey?: TeamKey;
    /** Signed: above zero reads hot, below reads cold. */
    value: number;
    note?: string;
    /** Replaces the caption while this row is hovered. */
    detail?: string;
}

interface DivergingRowsProps {
    rows: DivergingRow[];
    caption: string;
    legend: { down: string; up: string };
    format?: (value: number) => string;
}

const COLUMNS = 'minmax(0, 1.1fr) minmax(0, 1.4fr) 54px 84px';
const TRACK_HEIGHT = 12;

function signed(value: number): string {
    return `${value > 0 ? '+' : ''}${value.toFixed(1)}`;
}

function LegendKey({ colour, label }: { colour: string; label: string }) {
    return (
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
            <span style={{ width: 14, height: 8, borderRadius: 2, background: colour }} />
            <span className="kicker" style={{ color: 'var(--paper-dim)' }}>{label}</span>
        </span>
    );
}

// Scaled to the largest magnitude on screen, so the rows stay comparable.
export function DivergingRows({ rows, caption, legend, format = signed }: DivergingRowsProps) {
    const [hovered, setHovered] = useState<string | number | null>(null);
    const maxAbs = Math.max(...rows.map((row) => Math.abs(row.value)), 0);

    return (
        <div>
            <div style={{ display: 'flex', gap: 18, marginBottom: 14, flexWrap: 'wrap' }}>
                <LegendKey colour="var(--cold)" label={legend.down} />
                <LegendKey colour="var(--hot)" label={legend.up} />
            </div>

            <div>
                {rows.map((row, index) => {
                    const { side, widthPct } = diverging(row.value, maxAbs);
                    const colour = divergingColour(side);
                    const dimmed = hovered !== null && hovered !== row.id;

                    return (
                        <div
                            key={row.id}
                            onMouseEnter={() => setHovered(row.id)}
                            onMouseLeave={() => setHovered(null)}
                            style={{
                                display: 'grid',
                                gridTemplateColumns: COLUMNS,
                                alignItems: 'center',
                                gap: 12,
                                padding: '8px 0',
                                borderBottom: index === rows.length - 1 ? 'none' : '1px solid var(--line)',
                                opacity: dimmed ? 0.55 : 1,
                                transition: 'opacity 120ms',
                            }}
                        >
                            <div style={{ display: 'flex', alignItems: 'center', gap: 9, minWidth: 0, fontSize: 13 }}>
                                {row.teamKey !== undefined && <TeamChip team={row.teamKey} />}
                                <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={row.label}>
                                    {row.label}
                                </span>
                            </div>

                            <div style={{ position: 'relative', height: TRACK_HEIGHT, background: 'var(--panel-2)', borderRadius: 2 }}>
                                <div
                                    aria-hidden
                                    style={{ position: 'absolute', left: '50%', top: -3, bottom: -3, width: 1, background: 'var(--paper-faint)' }}
                                />
                                {/* Each side owns half the track, so a full-scale value fills 50%. */}
                                <div
                                    style={{
                                        position: 'absolute',
                                        top: 0,
                                        bottom: 0,
                                        width: `${widthPct / 2}%`,
                                        ...(side === 'up'
                                            ? { left: '50%', borderRadius: '0 2px 2px 0' }
                                            : { right: '50%', borderRadius: '2px 0 0 2px' }),
                                        background: `linear-gradient(${side === 'up' ? '90deg' : '270deg'}, color-mix(in srgb, ${colour} 35%, transparent), ${colour})`,
                                    }}
                                />
                            </div>

                            <span
                                style={{
                                    fontFamily: 'var(--mono)',
                                    fontSize: 13,
                                    fontWeight: 700,
                                    textAlign: 'right',
                                    color: colour,
                                    fontVariantNumeric: 'tabular-nums',
                                }}
                            >
                                {format(row.value)}
                            </span>

                            <span
                                style={{
                                    fontFamily: 'var(--mono)',
                                    fontSize: 11,
                                    textAlign: 'right',
                                    color: 'var(--paper-dim)',
                                    fontVariantNumeric: 'tabular-nums',
                                    overflow: 'hidden',
                                    whiteSpace: 'nowrap',
                                }}
                            >
                                {row.note ?? ''}
                            </span>
                        </div>
                    );
                })}
            </div>

            <div style={{ marginTop: 12, minHeight: 18, fontSize: 12, fontFamily: 'var(--mono)', color: 'var(--paper-dim)' }}>
                {hovered !== null && rows.find((row) => row.id === hovered)?.detail ? (
                    <span style={{ color: 'var(--paper)' }}>{rows.find((row) => row.id === hovered)?.detail}</span>
                ) : (
                    <span>{caption}</span>
                )}
            </div>
        </div>
    );
}
