import { useState } from 'react';
import type { ReactNode } from 'react';
import type { ConfidenceBucket } from '../../utils/modelStats';

interface CalibrationChartProps {
    buckets: ConfidenceBucket[];
}

const BAR_HEIGHT = 14;
const ROW_HEIGHT = BAR_HEIGHT + 6;
const GRID = [0, 25, 50, 75, 100];
const COLUMNS = '62px minmax(0, 1fr) 42px';

function LegendKey({ swatch, label }: { swatch: ReactNode; label: string }) {
    return (
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
            {swatch}
            <span className="kicker" style={{ color: 'var(--paper-dim)' }}>{label}</span>
        </span>
    );
}

/** Reliability plot: a bar short of its tick means the model oversold that band. */
export function CalibrationChart({ buckets }: CalibrationChartProps) {
    const [hovered, setHovered] = useState<number | null>(null);

    return (
        <div>
            <div style={{ display: 'flex', gap: 18, marginBottom: 16, flexWrap: 'wrap' }}>
                <LegendKey
                    label="Actually right"
                    swatch={<span style={{ width: 14, height: 8, borderRadius: '0 2px 2px 0', background: 'var(--worm)' }} />}
                />
                <LegendKey
                    label="Claimed confidence"
                    swatch={<span style={{ width: 2, height: 12, background: 'var(--paper)' }} />}
                />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                {buckets.map((bucket, index) => {
                    const empty = bucket.games === 0;
                    const dimmed = hovered !== null && hovered !== index;

                    return (
                        <div
                            key={bucket.floor}
                            onMouseEnter={() => setHovered(index)}
                            onMouseLeave={() => setHovered(null)}
                            style={{
                                display: 'grid',
                                gridTemplateColumns: COLUMNS,
                                alignItems: 'center',
                                gap: 12,
                                opacity: dimmed ? 0.55 : 1,
                                transition: 'opacity 120ms',
                            }}
                        >
                            <span className="kicker" style={{ color: 'var(--paper-dim)' }}>{bucket.label}</span>

                            <div style={{ position: 'relative', height: ROW_HEIGHT, display: 'flex', alignItems: 'center' }}>
                                <div style={{ position: 'absolute', inset: '3px 0', background: 'var(--panel-2)', borderRadius: 2 }} />

                                {GRID.slice(1, -1).map((tick) => (
                                    <div
                                        key={tick}
                                        aria-hidden
                                        style={{
                                            position: 'absolute',
                                            left: `${tick}%`,
                                            top: 0,
                                            bottom: 0,
                                            width: 1,
                                            background: 'var(--line)',
                                        }}
                                    />
                                ))}

                                {!empty && (
                                    <>
                                        <div
                                            style={{
                                                position: 'relative',
                                                height: BAR_HEIGHT,
                                                width: `${bucket.realised * 100}%`,
                                                background: 'var(--worm)',
                                                borderRadius: '0 4px 4px 0',
                                            }}
                                        />
                                        {/* Overhangs the track top and bottom so it reads as a
                                            target marker whether it lands on the bar or on the
                                            empty track, and is ringed in the surface colour so it
                                            stays legible crossing the bar. */}
                                        <div
                                            style={{
                                                position: 'absolute',
                                                left: `${bucket.claimed * 100}%`,
                                                top: -4,
                                                height: ROW_HEIGHT + 8,
                                                width: 2,
                                                marginLeft: -1,
                                                background: 'var(--paper)',
                                                // A ring, not borders: border-box leaves a
                                                // 2px-wide element no fill at all.
                                                boxShadow: '0 0 0 2px var(--panel)',
                                            }}
                                        />
                                    </>
                                )}

                                {empty && (
                                    <span style={{ position: 'relative', fontSize: 11, color: 'var(--paper-faint)', paddingLeft: 8 }}>
                                        no games
                                    </span>
                                )}
                            </div>

                            <span
                                style={{
                                    fontFamily: 'var(--mono)',
                                    fontSize: 13,
                                    fontWeight: 600,
                                    textAlign: 'right',
                                    color: empty ? 'var(--paper-faint)' : 'var(--paper)',
                                    fontVariantNumeric: 'tabular-nums',
                                }}
                            >
                                {empty ? '—' : `${Math.round(bucket.realised * 100)}%`}
                            </span>
                        </div>
                    );
                })}
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: COLUMNS, gap: 12, marginTop: 6 }}>
                <span />
                <div style={{ position: 'relative', height: 14 }}>
                    {GRID.map((tick) => (
                        <span
                            key={tick}
                            className="kicker"
                            style={{
                                position: 'absolute',
                                left: `${tick}%`,
                                transform: tick === 0 ? 'none' : tick === 100 ? 'translateX(-100%)' : 'translateX(-50%)',
                                color: 'var(--paper-faint)',
                            }}
                        >
                            {tick}%
                        </span>
                    ))}
                </div>
                <span />
            </div>

            <div style={{ marginTop: 12, minHeight: 18, fontSize: 12, fontFamily: 'var(--mono)', color: 'var(--paper-dim)' }}>
                {hovered !== null && buckets[hovered].games > 0 ? (
                    <span style={{ color: 'var(--paper)' }}>
                        {buckets[hovered].label}: {buckets[hovered].games} games · claimed{' '}
                        {Math.round(buckets[hovered].claimed * 100)}% · right{' '}
                        {Math.round(buckets[hovered].realised * 100)}%
                    </span>
                ) : (
                    <span>Bar short of the tick = the model oversold that band.</span>
                )}
            </div>
        </div>
    );
}
