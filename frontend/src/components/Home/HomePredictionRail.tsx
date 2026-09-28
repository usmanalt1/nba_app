import { PredictionBar } from '../ui/PredictionBar';
import { parseAwayTeam } from '../../utils/predictions';
import type { Prediction } from '../../types/predictions';

interface HomePredictionRailProps {
    predictions: Prediction[];
    empty?: string;
}

export function HomePredictionRail({ predictions, empty = 'Nothing to show yet.' }: HomePredictionRailProps) {
    if (predictions.length === 0) {
        return <div style={{ fontSize: 13, color: 'var(--paper-faint)', padding: '8px 0' }}>{empty}</div>;
    }

    return (
        <div className="rail">
            <div style={{ display: 'flex', gap: 14, width: 'max-content' }}>
                {predictions.map((prediction) => (
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
            </div>
        </div>
    );
}
