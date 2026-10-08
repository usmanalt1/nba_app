import { HomeTrends } from '../Home/HomeTrends';
import { HomeMostImproved } from '../Home/HomeMostImproved';
import { HomeTeamLeaders } from '../Home/HomeTeamLeaders';
import { HomeModelComparison } from '../Home/HomeModelComparison';
import { SectionHeader } from '../ui/SectionHeader';
import { WormPortrait } from '../ui/WormMark';
import { useStatsSeason } from '../../hooks/useStatsSeason';
import { env } from '../../env';

function AnalyticsHero({ statsSeason }: { statsSeason: string | null }) {
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
                        Season Breakdown
                    </div>
                    <h1
                        style={{
                            margin: 0,
                            fontSize: 'clamp(44px, 7vw, 80px)',
                            lineHeight: 0.85,
                            letterSpacing: '0.02em',
                            fontWeight: 700,
                            color: 'var(--paper)',
                        }}
                    >
                        Wormalytics
                    </h1>
                    <p style={{ marginTop: 14, fontSize: 15, color: 'var(--paper-dim)', maxWidth: 440 }}>
                        Who led, who climbed, and which model actually held up over a
                        full season of box scores.
                    </p>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                    <span className="kicker" style={{ color: 'var(--paper-faint)' }}>Stats from</span>
                    <span style={{ fontFamily: 'var(--mono)', fontSize: 13, color: 'var(--paper)' }}>
                        {statsSeason ?? env.VITE_DEFAULT_SEASON ?? '—'}
                    </span>
                </div>
            </div>

            <WormPortrait height={260} style={{ alignSelf: 'flex-end', marginRight: -12 }} />
        </section>
    );
}

export function Analytics() {
    const statsSeason = useStatsSeason();

    return (
        <div style={{ width: '100%', maxWidth: 1400, margin: '0 auto', paddingBottom: 60 }}>
            <AnalyticsHero statsSeason={statsSeason} />

            <section style={{ marginBottom: 'var(--section-gap)' }}>
                <SectionHeader
                    index="01"
                    title="Player Leaders"
                    subtitle={statsSeason ? `${statsSeason} season averages, ranked` : 'Season averages, ranked'}
                />
                <HomeTrends season={statsSeason} />
            </section>

            <section style={{ marginBottom: 'var(--section-gap)' }}>
                <SectionHeader
                    index="02"
                    title="Most Improved"
                    subtitle={statsSeason ? `Biggest jumps in ${statsSeason} against the season before` : 'Biggest jumps against last season'}
                />
                <HomeMostImproved />
            </section>

            <section style={{ marginBottom: 'var(--section-gap)' }}>
                <SectionHeader
                    index="03"
                    title="Team Leaders"
                    subtitle={statsSeason ? `${statsSeason} season averages, ranked` : 'Season averages, ranked'}
                />
                <HomeTeamLeaders season={statsSeason} />
            </section>

            <section>
                <SectionHeader
                    index="04"
                    title="Model Bench"
                    subtitle="Every run held against the same four metrics"
                />
                <HomeModelComparison />
            </section>
        </div>
    );
}
