import { HomeTrends } from '../Home/HomeTrends';
import { HomeMostImproved } from '../Home/HomeMostImproved';
import { HomeTeamLeaders } from '../Home/HomeTeamLeaders';
import { HomeModelComparison } from '../Home/HomeModelComparison';
import { SectionHeader } from '../ui/SectionHeader';
import { HeroStat, PageHero } from '../ui/PageHero';
import { useStatsSeason } from '../../hooks/useStatsSeason';
import { env } from '../../env';

function AnalyticsHero({ statsSeason }: { statsSeason: string | null }) {
    return (
        <PageHero
            eyebrow="Season Breakdown"
            title="Wormalytics"
            blurb="Who led, who climbed, and which model actually held up over a full season of box scores."
        >
            <HeroStat label="Stats from" value={statsSeason ?? env.VITE_DEFAULT_SEASON ?? '—'} />
        </PageHero>
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
