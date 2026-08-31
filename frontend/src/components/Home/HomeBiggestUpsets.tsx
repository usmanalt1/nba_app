import { Box, Group, ScrollArea, Text } from '@mantine/core';
import { usePredictions } from '../../hooks/usePredictions';
import { parseAwayTeam } from '../../utils/predictions';
import { PredictionBar } from '../ui/PredictionBar';
import type { Prediction } from '../../types/predictions';

function modelConfidence(prediction: Prediction): number {
    return prediction.predicted_home_win
        ? prediction.home_win_probability
        : 1 - prediction.home_win_probability;
}

export function HomeBiggestUpsets() {
    const { strategy, predictions } = usePredictions();

    const upsets = predictions
        .filter((prediction) => prediction.predicted_home_win !== prediction.actual_home_win)
        .sort((a, b) => modelConfidence(b) - modelConfidence(a))
        .slice(0, 8);

    if (!strategy || upsets.length === 0) return null;

    return (
        <Box style={{ marginBottom: '30px', width: '100%' }}>
            <Text
                size="10px"
                c="var(--paper-dim)"
                tt="uppercase"
                ff="'IBM Plex Mono', monospace"
                style={{ letterSpacing: '0.06em', marginBottom: 10 }}
            >
                Biggest Upsets — where {strategy} was most confident and wrong
            </Text>
            <ScrollArea scrollbars="x" type="always" w="100%" style={{ minWidth: 0 }}>
                <Group wrap="nowrap" gap="md">
                    {upsets.map((prediction) => (
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
