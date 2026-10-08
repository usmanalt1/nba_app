import type { ReactNode } from 'react';
import { WormPortrait } from './WormMark';

interface PageHeroProps {
    /** Short kicker above the title: "NBA Prediction Lab", "Season Breakdown". */
    eyebrow: string;
    title: string;
    blurb: string;
    /** For pages whose content wants the vertical room - a full-height table. */
    compact?: boolean;
    /** HeroStat entries laid out in a row under the blurb. */
    children?: ReactNode;
}

/** Label-over-value pair for a hero's meta row. */
export function HeroStat({ label, value }: { label: string; value: string }) {
    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            <span className="kicker" style={{ color: 'var(--paper-faint)' }}>{label}</span>
            <span style={{ fontFamily: 'var(--mono)', fontSize: 13, color: 'var(--paper)', textTransform: 'capitalize' }}>
                {value}
            </span>
        </div>
    );
}

/** The tall opening header every top-level page leads with, portrait and all. */
export function PageHero({ eyebrow, title, blurb, compact, children }: PageHeroProps) {
    return (
        <section
            style={{
                position: 'relative',
                display: 'flex',
                alignItems: 'stretch',
                justifyContent: 'space-between',
                gap: 24,
                overflow: 'hidden',
                borderBottom: '1px solid var(--line)',
                marginBottom: compact ? 20 : 'var(--section-gap)',
                minHeight: compact ? 120 : 200,
            }}
        >
            <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: compact ? 10 : 18, padding: compact ? '14px 0' : '24px 0', zIndex: 1 }}>
                <div>
                    <div className="kicker" style={{ color: 'var(--worm)', marginBottom: compact ? 6 : 10 }}>{eyebrow}</div>
                    {/* Clamped rather than fixed: a long title has to survive 1024px and below. */}
                    <h1
                        style={{
                            margin: 0,
                            fontSize: compact ? 'clamp(30px, 3.6vw, 46px)' : 'clamp(44px, 7vw, 92px)',
                            lineHeight: 0.85,
                            letterSpacing: '0.02em',
                            fontWeight: 700,
                            color: 'var(--paper)',
                        }}
                    >
                        {title}
                    </h1>
                    <p
                        style={{
                            marginTop: compact ? 8 : 14,
                            fontSize: compact ? 13 : 15,
                            color: 'var(--paper-dim)',
                            // Wider when compact, so the blurb stays on one or two lines.
                            maxWidth: compact ? 620 : 440,
                        }}
                    >
                        {blurb}
                    </p>
                </div>

                {children && <div style={{ display: 'flex', gap: 28, flexWrap: 'wrap' }}>{children}</div>}
            </div>

            <WormPortrait height={compact ? 150 : 260} style={{ alignSelf: 'flex-end', marginRight: -12 }} />
        </section>
    );
}
