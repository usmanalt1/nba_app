import { useEffect, useState } from "react";
import type { RankedPlayerStats } from '../../types/player';
import { Leaderboard, type LeaderboardRow } from '../ui/Leaderboard';
import { apiFetch } from '../../lib/api';
import { env } from '../../env';

type StatKey = 'points' | 'rebounds' | 'assists';

const STAT_CONFIG: Record<StatKey, { title: string; valueKey: keyof RankedPlayerStats; rankKey: keyof RankedPlayerStats }> = {
    points: { title: 'Points Per Game', valueKey: 'average_points', rankKey: 'rank_average_points' },
    rebounds: { title: 'Rebounds Per Game', valueKey: 'average_rebounds', rankKey: 'rank_average_rebounds' },
    assists: { title: 'Assists Per Game', valueKey: 'average_assists', rankKey: 'rank_average_assists' },
};

export function HomeTrends() {
    const [players, setPlayers] = useState<RankedPlayerStats[]>([]);

    useEffect(() => {
        apiFetch(`/api/nba/analytics/average_stats/season=${env.VITE_DEFAULT_SEASON}/season_type=${env.VITE_DEFAULT_SEASON_TYPE}`)
            .then(r => r.json())
            .then(data => setPlayers(data.records ?? []));
    }, []);

    const buildLeaderboardRows = (stat: StatKey): LeaderboardRow[] => {
        const { valueKey, rankKey } = STAT_CONFIG[stat];
        return [...players]
            .sort((a, b) => (a[rankKey] as number) - (b[rankKey] as number))
            .slice(0, 10)
            .map((player) => ({
                rank: player[rankKey] as number,
                label: player.player_name,
                sublabel: player.team_name,
                value: (player[valueKey] as number).toFixed(1),
            }));
    };

    return (
        <div style={{ marginBottom: '30px', width: '100%', display: 'grid', gridTemplateColumns: 'repeat(3, minmax(0, 1fr))', gap: '30px' }}>
            {(Object.keys(STAT_CONFIG) as StatKey[]).map((stat) => (
                <Leaderboard key={stat} title={STAT_CONFIG[stat].title} rows={buildLeaderboardRows(stat)} />
            ))}
        </div>
    );
}
