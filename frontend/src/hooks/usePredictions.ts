import { useEffect, useState } from 'react';
import type { Prediction } from '../types/predictions';
import { apiFetch } from '../lib/api';

interface PredictionsState {
    strategy: string | null;
    predictions: Prediction[];
}

export function usePredictions(): PredictionsState {
    const [strategy, setStrategy] = useState<string | null>(null);
    const [predictions, setPredictions] = useState<Prediction[]>([]);

    useEffect(() => {
        apiFetch('/api/nba/model/get_last_run')
            .then(r => r.json())
            .then(data => {
                if (!data.success) return;
                setStrategy(data.strategy);
                apiFetch(`/api/nba/model/get_ml_trained_models/${data.strategy}/${data.season}`)
                    .then(r => r.json())
                    .then(result => {
                        if (result.success) setPredictions(result.predictions ?? []);
                    });
            });
    }, []);

    return { strategy, predictions };
}
