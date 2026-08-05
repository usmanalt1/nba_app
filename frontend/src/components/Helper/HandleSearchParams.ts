import type { useSearchParams } from 'react-router-dom';

type SetSearchParams = ReturnType<typeof useSearchParams>[1];

export function handleSearchParams(setSearchParams: SetSearchParams, key: string, value: string | null) {
    setSearchParams(prev => {
        if (value) prev.set(key, value);
        else prev.delete(key);
        return prev;
    });
}