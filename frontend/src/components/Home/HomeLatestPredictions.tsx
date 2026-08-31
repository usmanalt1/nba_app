import { useEffect, useState } from 'react';
import { Box, Group, ScrollArea, Text } from '@mantine/core';
import type { Prediction } from '../../types/predictions';
import { PredictionBar } from '../ui/PredictionBar';

function parseAwayTeam(matchup: string, homeTeam: string): string {
    return matchup.replace(`${homeTeam} vs `, '').trim();
}

export function HomeLatestPredictions() {
    const [predictions, setPredictions] = useState<Prediction[]>([]);
    const [strategy, setStrategy] = useState<string | null>(null);

    useEffect(() => {
        fetch('/api/nba/model/get_last_run')
            .then(r => r.json())
            .then(data => {
                if (!data.success) return;
                setStrategy(data.strategy);
                fetch(`/api/nba/model/get_ml_trained_models/${data.strategy}/${data.season}`)
                    .then(r => r.json())
                    .then(result => {
                        if (result.success) setPredictions(result.predictions ?? []);
                    });
            });
    }, []);

    const latest = [...predictions]
        .sort((a, b) => new Date(b.game_date).getTime() - new Date(a.game_date).getTime())
        .slice(0, 8);

    if (!strategy || latest.length === 0) return null;

    return (
        <Box style={{ marginBottom: '30px', width: '100%' }}>
            <Text
                size="10px"
                c="var(--paper-dim)"
                tt="uppercase"
                ff="'IBM Plex Mono', monospace"
                style={{ letterSpacing: '0.06em', marginBottom: 10 }}
            >
                Model Predictions — {strategy}
            </Text>
            <ScrollArea scrollbars="x" type="always" w="100%" style={{ minWidth: 0 }}>
                <Group wrap="nowrap" gap="md">
                    {latest.map((prediction) => (
                        <PredictionBar
                            key={prediction.game_id}
                            homeTeam={prediction.home_team_name}
                            awayTeam={parseAwayTeam(prediction.matchup, prediction.home_team_name)}
                            homeWinProbability={prediction.home_win_probability}
                            predictedHomeWin={prediction.predicted_home_win}
                            actualHomeWin={prediction.actual_home_win}
                            gameDate={prediction.game_date}
                        />
                    ))}
                </Group>
            </ScrollArea>
        </Box>
    );
}
