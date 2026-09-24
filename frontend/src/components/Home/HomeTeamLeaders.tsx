import { useEffect, useState } from "react";
import type { RankedTeamStats } from '../../types/team';
import { Leaderboard, type LeaderboardRow } from '../ui/Leaderboard';

type StatKey = 'points' | 'rebounds' | 'assists';

const STAT_CONFIG: Record<StatKey, { title: string; valueKey: keyof RankedTeamStats; rankKey: keyof RankedTeamStats }> = {
    points: { title: 'Team Points Per Game', valueKey: 'average_points', rankKey: 'rank_average_points' },
    rebounds: { title: 'Team Rebounds Per Game', valueKey: 'average_rebounds', rankKey: 'rank_average_rebounds' },
    assists: { title: 'Team Assists Per Game', valueKey: 'average_assists', rankKey: 'rank_average_assists' },
};

export function HomeTeamLeaders() {
    const [teams, setTeams] = useState<RankedTeamStats[]>([]);

    useEffect(() => {
        fetch("/api/nba/analytics/average_team_stats")
            .then(r => r.json())
            .then(data => setTeams(data.records ?? []));
    }, []);

    const latestSeason = teams.reduce((latest, team) => (
        team.season > latest ? team.season : latest
    ), "");

    const regularSeasonTeams = teams.filter(
        (team) => team.season === latestSeason && !team.season_id.startsWith("42")
    );

    const buildLeaderboardRows = (stat: StatKey): LeaderboardRow[] => {
        const { valueKey, rankKey } = STAT_CONFIG[stat];
        return [...regularSeasonTeams]
            .sort((a, b) => (a[rankKey] as number) - (b[rankKey] as number))
            .slice(0, 10)
            .map((team) => ({
                rank: team[rankKey] as number,
                label: team.team_name,
                sublabel: `${(team.win_pct * 100).toFixed(0)}% win rate`,
                value: (team[valueKey] as number).toFixed(1),
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
