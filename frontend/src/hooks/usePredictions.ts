import { useEffect, useState } from 'react';
import type { Prediction } from '../types/predictions';

interface PredictionsState {
    strategy: string | null;
    predictions: Prediction[];
}

export function usePredictions(): PredictionsState {
    const [strategy, setStrategy] = useState<string | null>(null);
    const [predictions, setPredictions] = useState<Prediction[]>([]);

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

    return { strategy, predictions };
}
