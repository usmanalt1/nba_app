import { useCallback, useEffect, useState } from 'react';
import { apiFetch } from '../lib/api';
import type { ConversationExchange } from '../types/conversation';

interface ConversationState {
    exchanges: ConversationExchange[];
    error: string | null;
    loading: boolean;
}

const PENDING: ConversationState = { exchanges: [], error: null, loading: true };

/** The stored transcript, newest first. `reload` re-reads it after asking something. */
export function useConversation() {
    const [state, setState] = useState<ConversationState>(PENDING);
    const [reloads, setReloads] = useState(0);

    const reload = useCallback(() => setReloads((n) => n + 1), []);

    useEffect(() => {
        let cancelled = false;

        apiFetch('/api/nba/llm/get_conversation')
            .then(r => r.json())
            .then((data: { answers?: ConversationExchange[] }) => {
                if (cancelled) return;
                // An empty transcript comes back as success:false, so absent means empty.
                setState({ exchanges: [...(data.answers ?? [])].reverse(), error: null, loading: false });
            })
            .catch(() => {
                if (!cancelled) setState({ exchanges: [], error: 'Could not load the transcript.', loading: false });
            });

        return () => { cancelled = true; };
    }, [reloads]);

    return { ...state, reload };
}
