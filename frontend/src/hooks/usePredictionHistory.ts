import { useEffect, useState } from 'react';
import type { Prediction } from '../types/predictions';
import { apiFetch } from '../lib/api';

interface PredictionHistoryState {
    strategy: string | null;
    season: string | null;
    seasonType: string | null;
    predictions: Prediction[];
    loading: boolean;
}

/**
 * The season's full prediction record. A live run only predicts unplayed games and the
 * cached run is replaced nightly, so the track record lives in model_prediction_history.
 * Graded rows are the record; ungraded ones are the upcoming slate.
 */
export function usePredictionHistory(): PredictionHistoryState {
    const [state, setState] = useState<PredictionHistoryState>({
        strategy: null,
        season: null,
        seasonType: null,
        predictions: [],
        loading: true,
    });

    useEffect(() => {
        let cancelled = false;

        async function load() {
            try {
                const lastRun = await apiFetch('/api/nba/model/get_last_run').then(r => r.json());
                if (cancelled) return;
                if (!lastRun.success) {
                    setState(previous => ({ ...previous, loading: false }));
                    return;
                }

                const { strategy, season, season_type: seasonType } = lastRun;
                const history = await apiFetch(
                    `/api/nba/model/prediction_history/${strategy}/${season}/${seasonType}`,
                ).then(r => r.json());
                if (cancelled) return;

                setState({
                    strategy,
                    season,
                    seasonType,
                    predictions: history.success ? history.predictions ?? [] : [],
                    loading: false,
                });
            } catch {
                if (!cancelled) setState(previous => ({ ...previous, loading: false }));
            }
        }

        load();
        return () => { cancelled = true; };
    }, []);

    return state;
}
