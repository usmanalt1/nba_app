import { useEffect, useState } from 'react';
import type { Prediction } from '../types/predictions';
import { apiFetch } from '../lib/api';

/** Read in this order so the preseason is in play before the regular season starts. */
const SEASON_TYPES = ['preseason', 'regular'];

interface PredictionHistoryState {
    strategy: string | null;
    season: string | null;
    /** Season type of the soonest unplayed game. */
    upcomingSeasonType: string | null;
    /** Season type the graded record comes from, which is not always the same one. */
    gradedSeasonType: string | null;
    /** Both season types, soonest first. */
    upcoming: Prediction[];
    /** One season type's graded rows. Preseason and regular are never combined. */
    graded: Prediction[];
    loading: boolean;
}

const EMPTY: PredictionHistoryState = {
    strategy: null,
    season: null,
    upcomingSeasonType: null,
    gradedSeasonType: null,
    upcoming: [],
    graded: [],
    loading: true,
};

function latestDate(rows: Prediction[]): string {
    return rows.reduce((newest, row) => (row.game_date > newest ? row.game_date : newest), '');
}

export interface SeasonTypeRows {
    seasonType: string;
    rows: Prediction[];
}

type Selection = Pick<
    PredictionHistoryState, 'upcoming' | 'graded' | 'upcomingSeasonType' | 'gradedSeasonType'
>;

/**
 * Splits the season types into the upcoming slate, which spans both, and the graded
 * record, which comes from one: the two hit rates are different samples.
 */
export function selectHistory(sets: SeasonTypeRows[]): Selection {
    const upcoming = sets
        .flatMap(set => set.rows.filter(row => row.actual_home_win === null))
        .sort((a, b) => a.game_date.localeCompare(b.game_date));

    const graded = sets
        .map(set => ({ seasonType: set.seasonType, rows: set.rows.filter(row => row.actual_home_win !== null) }))
        .filter(set => set.rows.length > 0)
        .sort((a, b) => latestDate(b.rows).localeCompare(latestDate(a.rows)))[0];

    return {
        upcoming,
        graded: graded?.rows ?? [],
        upcomingSeasonType: upcoming[0]?.season_type ?? null,
        gradedSeasonType: graded?.seasonType ?? null,
    };
}

/**
 * The season's prediction record, read from model_prediction_history: the cached run is
 * replaced nightly. Both season types are read, as they come and go at different times.
 */
export function usePredictionHistory(): PredictionHistoryState {
    const [state, setState] = useState<PredictionHistoryState>(EMPTY);

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

                const { strategy, season } = lastRun;
                const sets: SeasonTypeRows[] = await Promise.all(SEASON_TYPES.map(async (seasonType) => {
                    const history = await apiFetch(
                        `/api/nba/model/prediction_history/${strategy}/${season}/${seasonType}`,
                    ).then(r => r.json()).catch(() => ({ success: false }));

                    return { seasonType, rows: history.success ? history.predictions ?? [] : [] };
                }));
                if (cancelled) return;

                const selection = selectHistory(sets);
                setState({
                    strategy,
                    season,
                    ...selection,
                    upcomingSeasonType: selection.upcomingSeasonType ?? lastRun.season_type ?? null,
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
