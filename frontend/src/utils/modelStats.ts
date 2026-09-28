import type { Prediction } from '../types/predictions';

export interface GradedPrediction extends Prediction {
    /** Probability the model assigned to the side it actually picked, always >= 0.5. */
    confidence: number;
    hit: boolean;
}

export interface ConfidenceBucket {
    /** Inclusive lower bound of the bucket, as a percentage (50, 60, ...). */
    floor: number;
    label: string;
    games: number;
    /** Mean confidence the model claimed across the bucket, 0-1. */
    claimed: number;
    /** Share of the bucket the model actually got right, 0-1. */
    realised: number;
}

export interface ModelStats {
    graded: GradedPrediction[];
    games: number;
    hits: number;
    misses: number;
    accuracy: number;
    /** Percentage points of accuracy above a coin flip. */
    edge: number;
    claimed: number;
    /** claimed - accuracy. Positive means the model talks a bigger game than it plays. */
    calibrationGap: number;
    homePickRate: number;
    homeWinRate: number;
    buckets: ConfidenceBucket[];
    /** Oldest-to-newest run of results, for the form strip. */
    form: GradedPrediction[];
    currentStreak: { length: number; hit: boolean } | null;
    bestStreak: number;
    /** Hit rate over the most recent N games, for the rolling-form readout. */
    rollingAccuracy: (window: number) => number | null;
}

const BUCKET_FLOORS = [50, 60, 70, 80, 90];

function byDateAscending(a: Prediction, b: Prediction): number {
    return new Date(a.game_date).getTime() - new Date(b.game_date).getTime();
}

function mean(values: number[]): number {
    if (values.length === 0) return 0;
    return values.reduce((total, value) => total + value, 0) / values.length;
}

/**
 * A prediction only tells us something once the game has been played. The API
 * returns `actual_home_win` as null for scheduled games in live mode, so anything
 * without a real boolean is dropped rather than silently graded as a loss.
 */
export function gradePredictions(predictions: Prediction[]): GradedPrediction[] {
    return predictions
        .filter((prediction) => typeof prediction.actual_home_win === 'boolean')
        .map((prediction) => ({
            ...prediction,
            confidence: prediction.predicted_home_win
                ? prediction.home_win_probability
                : 1 - prediction.home_win_probability,
            hit: prediction.predicted_home_win === prediction.actual_home_win,
        }));
}

function buildBuckets(graded: GradedPrediction[]): ConfidenceBucket[] {
    return BUCKET_FLOORS.map((floor, index) => {
        const ceiling = BUCKET_FLOORS[index + 1] ?? 101;
        const members = graded.filter((prediction) => {
            const pct = prediction.confidence * 100;
            return pct >= floor && pct < ceiling;
        });

        return {
            floor,
            label: floor === 90 ? '90–100%' : `${floor}–${ceiling}%`,
            games: members.length,
            claimed: mean(members.map((prediction) => prediction.confidence)),
            realised: members.length === 0
                ? 0
                : members.filter((prediction) => prediction.hit).length / members.length,
        };
    });
}

function buildStreaks(form: GradedPrediction[]) {
    let bestStreak = 0;
    let running = 0;

    for (const prediction of form) {
        running = prediction.hit ? running + 1 : 0;
        bestStreak = Math.max(bestStreak, running);
    }

    const newest = form[form.length - 1];
    if (!newest) return { currentStreak: null, bestStreak };

    let length = 0;
    for (let index = form.length - 1; index >= 0; index -= 1) {
        if (form[index].hit !== newest.hit) break;
        length += 1;
    }

    return { currentStreak: { length, hit: newest.hit }, bestStreak };
}

export function computeModelStats(predictions: Prediction[], formLength = 40): ModelStats {
    const graded = gradePredictions(predictions);
    const form = [...graded].sort(byDateAscending);
    const hits = graded.filter((prediction) => prediction.hit).length;
    const accuracy = graded.length === 0 ? 0 : hits / graded.length;
    const claimed = mean(graded.map((prediction) => prediction.confidence));
    const { currentStreak, bestStreak } = buildStreaks(form);

    return {
        graded,
        games: graded.length,
        hits,
        misses: graded.length - hits,
        accuracy,
        edge: (accuracy - 0.5) * 100,
        claimed,
        calibrationGap: claimed - accuracy,
        homePickRate: graded.length === 0
            ? 0
            : graded.filter((prediction) => prediction.predicted_home_win).length / graded.length,
        homeWinRate: graded.length === 0
            ? 0
            : graded.filter((prediction) => prediction.actual_home_win).length / graded.length,
        buckets: buildBuckets(graded),
        form: form.slice(-formLength),
        currentStreak,
        bestStreak,
        rollingAccuracy: (window: number) => {
            if (form.length < window) return null;
            const recent = form.slice(-window);
            return recent.filter((prediction) => prediction.hit).length / recent.length;
        },
    };
}
