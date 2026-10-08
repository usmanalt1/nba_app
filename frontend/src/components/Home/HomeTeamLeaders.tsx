import { useEffect, useState } from "react";
import type { RankedTeamStats } from '../../types/team';
import { Leaderboard, type LeaderboardRow } from '../ui/Leaderboard';
import { apiFetch } from '../../lib/api';
import { env } from '../../env';

type StatKey = 'points' | 'rebounds' | 'assists';

const STAT_CONFIG: Record<StatKey, { title: string; valueKey: keyof RankedTeamStats; rankKey: keyof RankedTeamStats }> = {
    points: { title: 'Team Points', valueKey: 'average_points', rankKey: 'rank_average_points' },
    rebounds: { title: 'Team Rebounds', valueKey: 'average_rebounds', rankKey: 'rank_average_rebounds' },
    assists: { title: 'Team Assists', valueKey: 'average_assists', rankKey: 'rank_average_assists' },
};

interface HomeTeamLeadersProps {
    /** null while the caller resolves it, which holds the fetch */
    season?: string | null;
    seasonType?: string;
    minGames?: number;
}

export function HomeTeamLeaders({ season, seasonType = 'regular', minGames = 0 }: HomeTeamLeadersProps = {}) {
    const [teams, setTeams] = useState<RankedTeamStats[]>([]);

    const seasonName = season ?? env.VITE_DEFAULT_SEASON;

    useEffect(() => {
        if (!seasonName) return;
        apiFetch(`/api/nba/analytics/average_team_stats/season=${seasonName}/season_type=${seasonType}?min_games=${minGames}`)
            .then(r => r.json())
            .then(data => setTeams(data.records ?? []))
            .catch(() => setTeams([]));
    }, [seasonName, seasonType, minGames]);

    const latestSeason = teams.reduce((latest, team) => (
        team.season > latest ? team.season : latest
    ), "");

    // Season type is the request's job now. The old `season_id.startsWith("42")` filter
    // re-derived it here and silently dropped every playoff row.
    const seasonTeams = teams.filter((team) => team.season === latestSeason);

    const buildLeaderboardRows = (stat: StatKey): LeaderboardRow[] => {
        const { valueKey, rankKey } = STAT_CONFIG[stat];
        return [...seasonTeams]
            .sort((a, b) => (a[rankKey] as number) - (b[rankKey] as number))
            .slice(0, 10)
            .map((team) => ({
                rank: team[rankKey] as number,
                label: team.team_name,
                sublabel: `${(team.win_pct * 100).toFixed(0)}% win rate`,
                value: (team[valueKey] as number).toFixed(1),
                magnitude: team[valueKey] as number,
            }));
    };

    return (
        <div style={{ width: '100%', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 20 }}>
            {(Object.keys(STAT_CONFIG) as StatKey[]).map((stat) => (
                <Leaderboard
                    key={stat}
                    title={STAT_CONFIG[stat].title}
                    titleMeta="per game"
                    rows={buildLeaderboardRows(stat)}
                />
            ))}
        </div>
    );
}
