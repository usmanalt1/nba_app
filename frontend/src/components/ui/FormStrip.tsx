import { useState } from 'react';
import type { GradedPrediction } from '../../utils/modelStats';
import { parseAwayTeam } from '../../utils/predictions';

interface FormStripProps {
    /** Oldest to newest. */
    form: GradedPrediction[];
}

const TRACK_HEIGHT = 48;
const MISS_HEIGHT = 17;

/**
 * A football-style form guide for the model. Hits are full-height, misses are
 * stubs, so the run reads correctly without relying on the red/green pair alone.
 */
export function FormStrip({ form }: FormStripProps) {
    const [hovered, setHovered] = useState<number | null>(null);
    const active = hovered === null ? null : form[hovered];

    return (
        <div style={{ position: 'relative' }}>
            <div
                style={{
                    display: 'flex',
                    alignItems: 'flex-end',
                    gap: 3,
                    height: TRACK_HEIGHT,
                    borderBottom: '1px solid var(--line)',
                    paddingBottom: 2,
                }}
            >
                {form.map((prediction, index) => (
                    <div
                        key={prediction.game_id}
                        onMouseEnter={() => setHovered(index)}
                        onMouseLeave={() => setHovered(null)}
                        // The hit target is the full-height column; the coloured tick inside
                        // it can be 11px tall without becoming impossible to hover.
                        style={{
                            flex: '1 1 0',
                            minWidth: 5,
                            maxWidth: 14,
                            height: TRACK_HEIGHT,
                            display: 'flex',
                            alignItems: 'flex-end',
                            cursor: 'default',
                        }}
                    >
                        <div
                            style={{
                                width: '100%',
                                height: prediction.hit ? TRACK_HEIGHT - 8 : MISS_HEIGHT,
                                borderRadius: '2px 2px 0 0',
                                background: prediction.hit ? 'var(--win)' : 'var(--lose)',
                                opacity: hovered === null || hovered === index ? 1 : 0.4,
                                transition: 'opacity 120ms',
                            }}
                        />
                    </div>
                ))}
            </div>

            <div
                style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    marginTop: 8,
                    fontSize: 11,
                    color: 'var(--paper-dim)',
                    fontFamily: 'var(--mono)',
                    minHeight: 16,
                }}
            >
                {active ? (
                    <span style={{ color: 'var(--paper)' }}>
                        {new Date(active.game_date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                        {'  '}
                        {parseAwayTeam(active.matchup, active.home_team_name)} @ {active.home_team_name}
                        {'  ·  '}
                        {Math.round(active.confidence * 100)}% confident
                        {'  ·  '}
                        <span style={{ color: active.hit ? 'var(--win)' : 'var(--lose)' }}>
                            {active.hit ? 'HIT' : 'MISS'}
                        </span>
                    </span>
                ) : (
                    <span>Oldest</span>
                )}
                {!active && <span>Newest</span>}
            </div>
        </div>
    );
}
