import { useEffect, useState } from 'react';
import { apiFetch } from '../lib/api';
import { env } from '../env';

interface SeasonOption {
    season_id: string;
    season_name: string;
}

/**
 * Newest season with recorded games - not the season the model predicts. The pipeline
 * follows the live season, which has no box scores until opening night, so pointing the
 * leaderboards at it would empty them every autumn. VITE_DEFAULT_SEASON overrides.
 */
export function useStatsSeason(): string | null {
    const override = env.VITE_DEFAULT_SEASON;
    const [season, setSeason] = useState<string | null>(override || null);

    useEffect(() => {
        if (override) return;

        let cancelled = false;
        apiFetch('/api/nba/db/list_all_seasons?has_stats=true')
            .then(r => r.json())
            .then((seasons: SeasonOption[]) => {
                if (cancelled || !Array.isArray(seasons) || seasons.length === 0) return;
                // returned in season order
                setSeason(seasons[seasons.length - 1].season_name);
            })
            .catch(() => { /* callers render their empty state */ });

        return () => { cancelled = true; };
    }, [override]);

    return season;
}
