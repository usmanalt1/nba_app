import { useEffect, useState } from 'react';
import { apiFetch } from '../lib/api';
import { env } from '../env';

interface SeasonOption {
    season_id: string;
    season_name: string;
}

/**
 * Newest season with recorded games, not the one the model predicts: the live season has
 * no box scores until opening night. VITE_DEFAULT_SEASON overrides.
 */
export function useStatsSeason(seasonType = 'regular'): string | null {
    const override = env.VITE_DEFAULT_SEASON;
    const [season, setSeason] = useState<string | null>(override || null);

    useEffect(() => {
        if (override) return;

        let cancelled = false;
        // Per season type: the newest playoff season isn't always the newest regular one.
        apiFetch(`/api/nba/db/list_all_seasons?has_stats=true&season_type=${seasonType}`)
            .then(r => r.json())
            .then((seasons: SeasonOption[]) => {
                if (cancelled || !Array.isArray(seasons) || seasons.length === 0) return;
                setSeason(seasons[seasons.length - 1].season_name);
            })
            .catch(() => { /* callers render their empty state */ });

        return () => { cancelled = true; };
    }, [override, seasonType]);

    return season;
}
