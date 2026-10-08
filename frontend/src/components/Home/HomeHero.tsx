import { WormPortrait } from '../ui/WormMark';
import { env } from '../../env';

interface HomeHeroProps {
    strategy: string | null;
    season?: string | null;
    seasonType?: string | null;
    statsSeason?: string | null;
}

function Chip({ label, value }: { label: string; value: string }) {
    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            <span className="kicker" style={{ color: 'var(--paper-faint)' }}>{label}</span>
            <span
                style={{
                    fontFamily: 'var(--mono)',
                    fontSize: 13,
                    color: 'var(--paper)',
                    textTransform: 'capitalize',
                }}
            >
                {value}
            </span>
        </div>
    );
}

export function HomeHero({ strategy, season, seasonType, statsSeason }: HomeHeroProps) {
    const predicting = [season ?? env.VITE_DEFAULT_SEASON, seasonType ?? env.VITE_DEFAULT_SEASON_TYPE]
        .filter(Boolean)
        .join(' ') || '—';

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
                marginBottom: 'var(--section-gap)',
                minHeight: 200,
            }}
        >
            <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', gap: 18, padding: '24px 0', zIndex: 1 }}>
                <div>
                    <div className="kicker" style={{ color: 'var(--worm)', marginBottom: 10 }}>
                        NBA Prediction Lab
                    </div>
                    <h1
                        style={{
                            margin: 0,
                            fontSize: 92,
                            lineHeight: 0.85,
                            letterSpacing: '0.02em',
                            fontWeight: 700,
                            color: 'var(--paper)',
                        }}
                    >
                        Worm
                    </h1>
                    <p style={{ marginTop: 14, fontSize: 15, color: 'var(--paper-dim)', maxWidth: 440 }}>
                        Chasing the loose ball in the box score. Models, calls and the stats
                        nobody puts on a highlight reel.
                    </p>
                </div>

                <div style={{ display: 'flex', gap: 28, flexWrap: 'wrap' }}>
                    {/* Two seasons on purpose: the model predicts the live one, the
                        leaderboards show the last with a full record. */}
                    <Chip label="Predicting" value={predicting} />
                    <Chip label="Stats from" value={statsSeason ?? env.VITE_DEFAULT_SEASON ?? '—'} />
                    <Chip label="Model" value={strategy ? strategy.replace(/_/g, ' ') : '—'} />
                </div>
            </div>

            <WormPortrait height={260} style={{ alignSelf: 'flex-end', marginRight: -12 }} />
        </section>
    );
}
