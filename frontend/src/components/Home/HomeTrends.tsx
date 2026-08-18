import { useEffect, useState } from "react";
import type { RankedPlayerStats } from '../../types/player';
import { Box } from '@mantine/core';


export function HomeTrends() {
    const [players, setPlayers] = useState<RankedPlayerStats[]>([]);

    const parseAverage = (data: { records: RankedPlayerStats[] }): RankedPlayerStats[] => data.records
    const latestSeason = players.reduce((latest, player) => {
        return player.season > latest ? player.season : latest;
    }, "");

    const parseAveragePoints = (): { season: string; season_id: string; player_name: string; rank_average_points: number; average_points: number }[] => {
        return players.filter((player) => player.season === latestSeason).filter((player) => !player.season_id.startsWith("42")).map((player) => ({
            season: player.season,
            season_id: player.season_id,
            player_name: player.player_name,
            rank_average_points: player.rank_average_points,
            average_points: player.average_points
        })).sort((a, b) => a.rank_average_points - b.rank_average_points);
    };
    

    useEffect(() => {
        fetch("/api/nba/analytics/average_stats")
            .then(r => r.json())
            .then(data => setPlayers(parseAverage(data)));
    }, []);

    return (
        <div style={{ marginBottom: '30px', width: '100%', display: 'flex', justifyContent: 'left' , gap: '30px', flexWrap: 'wrap' }}>
            <Box 
                w={{ base: '100%', lg: 400 }} 
                h={400} 
                p="xl" 
                bg="var(--panel)"
                c="var(--paper)"
                >
                <div style={{ textAlign: 'center', padding: '10px' }}>
                    {parseAveragePoints().map((player, index) => (
                        <div key={index} style={{ marginBottom: '10px', fontWeight: 500, fontSize: '110%', color: 'var(--paper)' }}>
                            {index === 0 && <strong>{player.player_name} - Rank {player.rank_average_points} - {player.season} - {player.average_points}</strong>}
                        </div>
                    ))}
                </div>
            </Box>
        </div>
    );
}
