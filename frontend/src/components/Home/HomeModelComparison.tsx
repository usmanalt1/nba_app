import { useEffect, useState } from 'react';
import type { ModelRunSummary } from '../../types/predictions';
import { apiFetch } from '../../lib/api';

const COLUMNS = [
    { key: 'accuracy', label: 'Accuracy', format: (v: number) => `${(v * 100).toFixed(1)}%`, higherIsBetter: true },
    { key: 'auc', label: 'AUC', format: (v: number) => v.toFixed(3), higherIsBetter: true },
    { key: 'log_loss', label: 'Log loss', format: (v: number) => v.toFixed(3), higherIsBetter: false },
    { key: 'brier', label: 'Brier', format: (v: number) => v.toFixed(3), higherIsBetter: false },
] as const;

const cell: React.CSSProperties = {
    padding: '10px 12px',
    fontFamily: 'var(--mono)',
    fontSize: 13,
    fontVariantNumeric: 'tabular-nums',
    borderBottom: '1px solid var(--line)',
};

export function HomeModelComparison() {
    const [runs, setRuns] = useState<ModelRunSummary[]>([]);

    useEffect(() => {
        apiFetch('/api/nba/model/get_all_runs')
            .then(r => r.json())
            .then(data => setRuns(data.runs ?? []))
            .catch(() => setRuns([]));
    }, []);

    if (runs.length === 0) return null;

    // The winner of each metric gets the accent, so a reader can scan one column and
    // see which run leads without comparing every number by eye.
    const leaders = Object.fromEntries(
        COLUMNS.map(({ key, higherIsBetter }) => [
            key,
            runs.reduce((best, run) => {
                const value = run.metrics[key];
                const bestValue = best.metrics[key];
                return (higherIsBetter ? value > bestValue : value < bestValue) ? run : best;
            }, runs[0]),
        ]),
    ) as Record<string, ModelRunSummary>;

    return (
        <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: 560 }}>
                <thead>
                    <tr>
                        <th style={{ ...cell, textAlign: 'left' }} className="kicker">Model</th>
                        <th style={{ ...cell, textAlign: 'left' }} className="kicker">Season</th>
                        {COLUMNS.map(({ key, label, higherIsBetter }) => (
                            <th key={key} style={{ ...cell, textAlign: 'right' }} className="kicker">
                                {label} {higherIsBetter ? '↑' : '↓'}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {runs.map((run) => (
                        <tr key={`${run.strategy}-${run.season}-${run.season_type}`}>
                            <td style={{ ...cell, color: 'var(--paper)', textTransform: 'capitalize' }}>
                                {run.strategy.replace(/_/g, ' ')}
                            </td>
                            <td style={{ ...cell, color: 'var(--paper-dim)' }}>
                                {run.season}
                                {run.season_type ? ` · ${run.season_type}` : ''}
                            </td>
                            {COLUMNS.map(({ key, format }) => {
                                const isLeader = runs.length > 1 && leaders[key] === run;
                                return (
                                    <td
                                        key={key}
                                        style={{
                                            ...cell,
                                            textAlign: 'right',
                                            color: isLeader ? 'var(--worm)' : 'var(--paper)',
                                            fontWeight: isLeader ? 600 : 400,
                                        }}
                                    >
                                        {format(run.metrics[key])}
                                    </td>
                                );
                            })}
                        </tr>
                    ))}
                </tbody>
            </table>
            {runs.length > 1 && (
                <div style={{ fontSize: 12, color: 'var(--paper-faint)', marginTop: 10 }}>
                    Best value in each column is highlighted. ↑ higher is better, ↓ lower is better.
                </div>
            )}
        </div>
    );
}
