import { Games } from  "../ScrollableGames/Games";
import { HomeTrends } from "./HomeTrends";
import { HomeTeamLeaders } from "./HomeTeamLeaders";
import { HomeMostImproved } from "./HomeMostImproved";
import { HomeLatestPredictions } from "./HomeLatestPredictions";
import { HomeBiggestUpsets } from "./HomeBiggestUpsets";
import { HomeModelComparison } from "./HomeModelComparison";

export function Home() {
    return (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
            <div style={{ marginBottom: '30px', width: '100%', display: 'flex', justifyContent: 'left' }}>
                <Games />
            </div>

            <HomeLatestPredictions />
            <HomeBiggestUpsets />
            <HomeModelComparison />

            <h2 style={{ width: '100%' }}>Player Leaders</h2>
            <HomeTrends />

            <h2 style={{ width: '100%' }}>Team Leaders</h2>
            <HomeTeamLeaders />

            <h2 style={{ width: '100%' }}>Most Improved</h2>
            <HomeMostImproved />
        </div>
    );
}
