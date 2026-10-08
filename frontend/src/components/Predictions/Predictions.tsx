import { useEffect, useState } from 'react';
import { Select, Button, Tabs } from "@mantine/core";
import 'mantine-datatable/styles.layer.css';
import { StandingsTable } from './StandingsTable';
import { PredictionsTable } from './PredictionsTable';
import { PageHero } from '../ui/PageHero';
import { Panel } from '../ui/Panel';
import { SectionHeader } from '../ui/SectionHeader';
import { StatCard } from '../ui/StatCard';
import type { TrainResponse } from '../../types/predictions';
import { useSearchParams } from 'react-router-dom';
import { handleSearchParams } from '../Helper/HandleSearchParams';
import { apiFetch } from '../../lib/api';


export function Predictions() {

    const [models, setModels] = useState<{ model_name: string }[]>([]);
    const [seasons, setSeasons] = useState([]);
    const [buttonActive, setButtonActive] = useState(false);
    const [searchParams, setSearchParams] = useSearchParams();
    const [result, setResult] = useState<TrainResponse | null>(null);

    const selectedModel = searchParams.get('model');
    const selectedSeason = searchParams.get('season');
    const selectedSeasonType = searchParams.get('season_type');
    const selectedMode = searchParams.get('mode') ?? 'backtest';
    const predictionsTab = searchParams.get('predictions_tab');

    useEffect(() => {
        apiFetch("/api/nba/model/get_ml_models")
            .then(r => r.json())
            .then(data => setModels(data.models ?? []));
    }, []);

    useEffect(() => {
        apiFetch("/api/nba/db/list_all_seasons")
            .then(r => r.json())
            .then(setSeasons);
    }, []);

    useEffect(() => {
        if (!selectedModel || !selectedSeason || !selectedSeasonType) return;

        apiFetch(`/api/nba/model/get_ml_trained_models/${selectedModel}/${selectedSeason}`)
            .then(r => r.json())
            .then(data => {
                if (data.success) setResult(data);
            });
    }, [selectedModel, selectedSeason, selectedSeasonType]);

    useEffect(() => {
        if (selectedModel || selectedSeason || selectedSeasonType) return;

        apiFetch("/api/nba/model/get_last_run")
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    setSearchParams(prev => {
                        prev.set('model', data.strategy);
                        prev.set('season', data.season);
                        prev.set('season_type', data.season_type);
                        prev.set('mode', data.mode ?? 'backtest');
                        prev.set('predictions_tab', 'standings');
                        return prev;
                    });
                }
            });
    }, []);

    const modelOptions = models.map((p) => ({
        value: String(p.model_name),
        label: String(p.model_name),
    }));

    const seasonOptions = seasons.map((p: any) => ({
        value: String(p.season_name),
        label: String(p.season_name),
    }));

    const handleRunModel = async () => {
        if (!selectedModel || !selectedSeason || !selectedSeasonType) return;

        setButtonActive(true);
        try {
            const response = await apiFetch(`/api/nba/model/train/${selectedModel}/${selectedSeason}/${selectedSeasonType}?mode=${selectedMode}`);
            const data = await response.json();
            setResult(data);
        } finally {
            setButtonActive(false);
        }
    };

    const handleSearchParamsChange = (key: string, value: string | null) => {
        handleSearchParams(setSearchParams, key, value);
    };

    const tabTypes = [
        { value: 'standings', label: 'Standings' },
        { value: 'predictions', label: 'Predictions' },
    ];

    return <div style={{ width: '100%', maxWidth: 1400, margin: '0 auto', paddingBottom: 60 }}>
        <PageHero
            eyebrow="Backtests & Calls"
            title="Wormhole"
            blurb="Run a model over a season and see what it would have called, graded against what actually happened."
        />

        <section style={{ marginBottom: 'var(--section-gap)' }}>
            <SectionHeader
                index="01"
                title="Set Up a Run"
                subtitle="Pick a model and a season, then run it over those games"
            />
            <Panel accent>
                <div style={{ display: 'flex', alignItems: 'flex-end', gap: 16, flexWrap: 'wrap' }}>
                    <Select
                        style={{ flex: 1, minWidth: 150 }}
                        label="Season"
                        placeholder="Pick a Season"
                        data={seasonOptions}
                        value={selectedSeason}
                        onChange={(value) => handleSearchParamsChange('season', value)}
                        searchable
                    />
                    <Select
                        style={{ flex: 1, minWidth: 150 }}
                        label="Season Type"
                        placeholder="Pick a Season Type"
                        data={[
                            { value: "regular", label: "Regular" },
                            { value: "playoffs", label: "Playoffs" },
                            { value: "preseason", label: "Preseason" },
                        ]}
                        value={selectedSeasonType}
                        onChange={(value) => handleSearchParamsChange('season_type', value)}
                        searchable
                    />
                    <Select
                        style={{ flex: 1, minWidth: 150 }}
                        label="ML Model"
                        placeholder="Pick a Model"
                        data={modelOptions}
                        value={selectedModel}
                        onChange={(value) => handleSearchParamsChange('model', value)}
                        searchable
                    />
                    <Select
                        style={{ flex: 1, minWidth: 150 }}
                        label="Mode"
                        data={[
                            { value: "backtest", label: "Backtest" },
                            { value: "live", label: "Live (in-season)" },
                        ]}
                        value={selectedMode}
                        onChange={(value) => handleSearchParamsChange('mode', value)}
                    />
                    <Button
                        variant="filled"
                        onClick={handleRunModel}
                        loading={buttonActive}
                        disabled={!selectedModel || !selectedSeason || !selectedSeasonType}
                    >
                        Run Model
                    </Button>
                </div>

                {result && !result.success && (
                    <div style={{ fontSize: 13, color: 'var(--lose)', paddingTop: 14 }}>
                        {result.error ?? 'That run did not come back.'}
                    </div>
                )}
            </Panel>
        </section>

        {result && result.success && result.metrics && (
            <section style={{ marginBottom: 'var(--section-gap)' }}>
                <SectionHeader
                    index="02"
                    title="Scorecard"
                    subtitle="How the run scored against the games it had not seen"
                />
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))', gap: 14 }}>
                    <StatCard
                        hero
                        tone="brand"
                        label="Accuracy"
                        value={`${(result.metrics.accuracy * 100).toFixed(1)}%`}
                        note="Share of games called right"
                    />
                    <StatCard hero label="AUC" value={result.metrics.auc.toFixed(3)} note="1.0 is perfect, 0.5 is a coin flip" />
                    <StatCard hero label="Log loss" value={result.metrics.log_loss.toFixed(3)} note="Lower is better; punishes confident misses" />
                    <StatCard hero label="Brier" value={result.metrics.brier.toFixed(3)} note="Lower is better; squared error on the probabilities" />
                </div>
            </section>
        )}

        <section style={{ marginBottom: 'var(--section-gap)' }}>
            <SectionHeader
                index={result && result.success && result.metrics ? '03' : '02'}
                title="Standings & Calls"
                subtitle="The season the run produced, and every game it called"
            />

            {!result && (
                <div style={{ fontSize: 13, color: 'var(--paper-faint)', padding: '8px 0' }}>
                    Nothing run yet. Pick a model and a season above.
                </div>
            )}

            {result && result.success && (
                <>
                    {/* Default variant: theme.ts already gives tabs the mono uppercase register. */}
                    <Tabs
                        value={predictionsTab}
                        onChange={(value) => handleSearchParamsChange('predictions_tab', value)}
                        style={{ marginBottom: 18 }}
                    >
                        <Tabs.List>
                            {tabTypes.map(type => (
                                <Tabs.Tab key={type.value} value={type.value}>{type.label}</Tabs.Tab>
                            ))}
                        </Tabs.List>
                    </Tabs>

                    {predictionsTab === 'standings' && (
                        result.season_records && result.season_records.length > 0
                            ? <StandingsTable records={result.season_records} />
                            : <div style={{ fontSize: 13, color: 'var(--paper-faint)', padding: '8px 0' }}>No season record came back from this run.</div>
                    )}

                    {predictionsTab !== 'standings' && (
                        result.predictions && result.predictions.length > 0
                            ? <PredictionsTable records={result.predictions} />
                            : <div style={{ fontSize: 13, color: 'var(--paper-faint)', padding: '8px 0' }}>No calls came back from this run.</div>
                    )}
                </>
            )}
        </section>
    </div>


}
