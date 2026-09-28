import { useMemo } from 'react';
import { Games } from '../ScrollableGames/Games';
import { HomeHero } from './HomeHero';
import { HomeModelPulse } from './HomeModelPulse';
import { HomePredictionRail } from './HomePredictionRail';
import { HomeTrends } from './HomeTrends';
import { HomeTeamLeaders } from './HomeTeamLeaders';
import { HomeMostImproved } from './HomeMostImproved';
import { HomeModelComparison } from './HomeModelComparison';
import { SectionHeader } from '../ui/SectionHeader';
import { usePredictions } from '../../hooks/usePredictions';
import { computeModelStats } from '../../utils/modelStats';

export function Home() {
    // Fetched once here and passed down: the tape, both rails and the hero all read
    // the same run, and three copies of this hook meant three round trips.
    const { strategy, predictions } = usePredictions();
    const stats = useMemo(() => computeModelStats(predictions), [predictions]);

    const latest = useMemo(
        () => [...predictions]
            .sort((a, b) => new Date(b.game_date).getTime() - new Date(a.game_date).getTime())
            .slice(0, 10),
        [predictions],
    );

    const upsets = useMemo(
        () => stats.graded
            .filter((prediction) => !prediction.hit)
            .sort((a, b) => b.confidence - a.confidence)
            .slice(0, 10),
        [stats.graded],
    );

    const modelName = strategy?.replace(/_/g, ' ');

    return (
        <div style={{ width: '100%', maxWidth: 1400, margin: '0 auto', paddingBottom: 60 }}>
            <HomeHero strategy={strategy} />

            <HomeModelPulse strategy={strategy} stats={stats} />

            <section style={{ marginBottom: 'var(--section-gap)' }}>
                <SectionHeader
                    index="02"
                    title="Around the League"
                    subtitle="Most recent final scores"
                />
                <Games />
            </section>

            <section style={{ marginBottom: 'var(--section-gap)' }}>
                <SectionHeader
                    index="03"
                    title="Latest Calls"
                    subtitle={modelName ? `What ${modelName} said about the most recent slate` : 'Most recent predictions'}
                />
                <HomePredictionRail predictions={latest} empty="No predictions for this run yet." />
            </section>

            <section style={{ marginBottom: 'var(--section-gap)' }}>
                <SectionHeader
                    index="04"
                    title="Burned"
                    subtitle="The games it was most sure about and still got wrong"
                />
                <HomePredictionRail predictions={upsets} empty="No misses on record — yet." />
            </section>

            <section style={{ marginBottom: 'var(--section-gap)' }}>
                <SectionHeader
                    index="05"
                    title="Player Leaders"
                    subtitle="Season averages, ranked"
                />
                <HomeTrends />
            </section>

            <section style={{ marginBottom: 'var(--section-gap)' }}>
                <SectionHeader
                    index="06"
                    title="Most Improved"
                    subtitle="Biggest jumps against last season"
                />
                <HomeMostImproved />
            </section>

            <section style={{ marginBottom: 'var(--section-gap)' }}>
                <SectionHeader
                    index="07"
                    title="Team Leaders"
                    subtitle="Season averages, ranked"
                />
                <HomeTeamLeaders />
            </section>

            <section>
                <SectionHeader
                    index="08"
                    title="Model Bench"
                    subtitle="Every run held against the same four metrics"
                />
                <HomeModelComparison />
            </section>
        </div>
    );
}
