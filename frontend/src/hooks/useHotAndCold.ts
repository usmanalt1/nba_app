import { useEffect, useState } from 'react';
import { apiFetch } from '../lib/api';
import type { HotColdResponse } from '../types/hotCold';

interface FormState {
    data: HotColdResponse | null;
    error: string | null;
    loading: boolean;
}

const PENDING: FormState = { data: null, error: null, loading: true };

/** The endpoint picks the season itself, so there is nothing to pass but the type. */
export function useHotAndCold(seasonType = 'regular', limit = 5) {
    // Written only from the fetch callbacks; the effect body would re-render too early.
    const [state, setState] = useState<FormState>(PENDING);

    useEffect(() => {
        let cancelled = false;

        apiFetch(`/api/nba/analytics/hot_and_cold?season_type=${seasonType}&limit=${limit}`)
            .then(r => r.json())
            .then((response: HotColdResponse) => {
                if (cancelled) return;
                setState(response.success
                    ? { data: response, error: null, loading: false }
                    : { data: null, error: response.error ?? 'Could not load form.', loading: false });
            })
            .catch(() => {
                if (!cancelled) setState({ data: null, error: 'Could not load form.', loading: false });
            });

        return () => { cancelled = true; };
    }, [seasonType, limit]);

    return state;
}
