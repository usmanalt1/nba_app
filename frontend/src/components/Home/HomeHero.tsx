import { HeroStat, PageHero } from '../ui/PageHero';
import { env } from '../../env';

interface HomeHeroProps {
    strategy: string | null;
    season?: string | null;
    seasonType?: string | null;
    statsSeason?: string | null;
}

export function HomeHero({ strategy, season, seasonType, statsSeason }: HomeHeroProps) {
    const predicting = [season ?? env.VITE_DEFAULT_SEASON, seasonType ?? env.VITE_DEFAULT_SEASON_TYPE]
        .filter(Boolean)
        .join(' ') || '—';

    return (
        <PageHero
            eyebrow="NBA Prediction Lab"
            title="Worm"
            blurb="Chasing the loose ball in the box score. Models, calls and the stats nobody puts on a highlight reel."
        >
            {/* Two seasons on purpose: the model predicts the live one, the leaderboards
                show the last with a full record. */}
            <HeroStat label="Predicting" value={predicting} />
            <HeroStat label="Stats from" value={statsSeason ?? env.VITE_DEFAULT_SEASON ?? '—'} />
            <HeroStat label="Model" value={strategy ? strategy.replace(/_/g, ' ') : '—'} />
        </PageHero>
    );
}
