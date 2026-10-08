import { HomeTrends } from '../Home/HomeTrends';
import { HomeMostImproved } from '../Home/HomeMostImproved';
import { HomeTeamLeaders } from '../Home/HomeTeamLeaders';
import { HomeModelComparison } from '../Home/HomeModelComparison';
import { SegmentedControl } from '@mantine/core';
import { SectionHeader } from '../ui/SectionHeader';
import { HeroStat, PageHero } from '../ui/PageHero';
import { useViewDataFilters } from '../ViewData/ViewDataFiltersContext';
import { STAGES, STAGE_TO_SEASON_TYPE, type Stage } from '../ViewData/stages';
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

/** A postseason run is a handful of games, so a rank needs more than a cameo behind it. */
const MIN_GAMES: Record<Stage, number> = { Regular: 0, Playoffs: 5, Preseason: 3 };

export function Analytics() {
    // Shared with View Data rather than local state, so the stage follows you across
    // the app instead of each page holding its own idea of it.
    const { selectedStage, setSelectedStage } = useViewDataFilters();
    const seasonType = STAGE_TO_SEASON_TYPE[selectedStage];
    const statsSeason = useStatsSeason(seasonType);
    const minGames = MIN_GAMES[selectedStage];

    const stage = (
        <SegmentedControl
            size="xs"
            value={selectedStage}
            onChange={(value) => setSelectedStage(value as Stage)}
            data={STAGES}
        />
    );
    const label = statsSeason ? `${statsSeason} ${selectedStage.toLowerCase()}` : selectedStage.toLowerCase();

    return (
        <div style={{ width: '100%', maxWidth: 1400, margin: '0 auto', paddingBottom: 60 }}>
            <AnalyticsHero statsSeason={statsSeason} />

            <section style={{ marginBottom: 'var(--section-gap)' }}>
                <SectionHeader
                    index="01"
                    title="Player Leaders"
                    subtitle={`${label} averages, ranked`}
                    meta={stage}
                />
                <HomeTrends season={statsSeason} seasonType={seasonType} minGames={minGames} />
            </section>

            <section style={{ marginBottom: 'var(--section-gap)' }}>
                <SectionHeader
                    index="02"
                    title="Most Improved"
                    subtitle={statsSeason ? `Biggest jumps in ${statsSeason} against the season before` : 'Biggest jumps against last season'}
                />
                <HomeMostImproved seasonType={seasonType} />
            </section>

            <section style={{ marginBottom: 'var(--section-gap)' }}>
                <SectionHeader
                    index="03"
                    title="Team Leaders"
                    subtitle={`${label} averages, ranked`}
                    meta={stage}
                />
                <HomeTeamLeaders season={statsSeason} seasonType={seasonType} minGames={minGames} />
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
