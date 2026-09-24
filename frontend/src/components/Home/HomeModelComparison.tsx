import { useEffect, useState } from 'react';
import { SimpleGrid, Text } from '@mantine/core';
import { StatTile } from '../Predictions/StatTile';
import type { ModelRunSummary } from '../../types/predictions';

export function HomeModelComparison() {
    const [runs, setRuns] = useState<ModelRunSummary[]>([]);

    useEffect(() => {
        fetch('/api/nba/model/get_all_runs')
            .then(r => r.json())
            .then(data => setRuns(data.runs ?? []));
    }, []);

    if (runs.length === 0) return null;

    return (
        <div style={{ marginBottom: '30px', width: '100%' }}>
            <Text
                size="10px"
                c="var(--paper-dim)"
                tt="uppercase"
                ff="'IBM Plex Mono', monospace"
                style={{ letterSpacing: '0.06em', marginBottom: 10 }}
            >
                Model Comparison
            </Text>
            <div
                style={{
                    display: 'grid',
                    gridTemplateColumns: `repeat(${Math.min(runs.length, 2)}, minmax(0, 1fr))`,
                    gap: '30px',
                }}
            >
                {runs.map((run) => (
                    <div key={`${run.strategy}-${run.season}`}>
                        <Text
                            size="14px"
                            fw={600}
                            c="var(--paper)"
                            ff="'IBM Plex Mono', monospace"
                            style={{ marginBottom: 10, textTransform: 'capitalize' }}
                        >
                            {run.strategy.replace(/_/g, ' ')}
                            <span style={{ color: 'var(--paper-dim)', fontWeight: 400 }}> — {run.season}</span>
                        </Text>
                        <SimpleGrid cols={2} spacing="sm">
                            <StatTile label="Accuracy" value={`${(run.metrics.accuracy * 100).toFixed(1)}%`} />
                            <StatTile label="AUC" value={run.metrics.auc.toFixed(3)} />
                            <StatTile label="Log Loss" value={run.metrics.log_loss.toFixed(3)} />
                            <StatTile label="Brier" value={run.metrics.brier.toFixed(3)} />
                        </SimpleGrid>
                    </div>
                ))}
            </div>
        </div>
    );
}
