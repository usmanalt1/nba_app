import { useEffect, useState } from 'react';
import { Select, Button, SimpleGrid, Text, Tabs } from "@mantine/core";
import 'mantine-datatable/styles.layer.css';
import { StatTile } from './StatTile';
import { StandingsTable } from './StandingsTable';
import { PredictionsTable } from './PredictionsTable';
import type { PredictionsProps, TrainResponse } from '../../types/predictions';
import { useSearchParams } from 'react-router-dom';


export function Predictions(props: PredictionsProps) {

    const [models, setModels] = useState<{ model_name: string }[]>([]);
    const [seasons, setSeasons] = useState([]);
    const [buttonActive, setButtonActive] = useState(false);
    const [searchParams, setSearchParams] = useSearchParams();
    const [result, setResult] = useState<TrainResponse | null>(null);

    const selectedModel = searchParams.get('model');
    const selectedSeason = searchParams.get('season');

    useEffect(() => {
        fetch("/api/nba/model/get_ml_models")
            .then(r => r.json())
            .then(data => setModels(data.models ?? []));
    }, []);

    useEffect(() => {
        fetch("/api/nba/db/list_all_seasons")
            .then(r => r.json())
            .then(setSeasons);
    }, []);

    useEffect(() => {
        if (!selectedModel || !selectedSeason) return;

        fetch(`/api/nba/model/get_ml_trained_models/${selectedModel}/${selectedSeason}`)
            .then(r => r.json())
            .then(data => {
                if (data.success) setResult(data);
            });
    }, [selectedModel, selectedSeason]);

    useEffect(() => {
        if (selectedModel || selectedSeason) return;

        fetch("/api/nba/model/get_last_run")
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    setSearchParams(prev => {
                        prev.set('model', data.strategy);
                        prev.set('season', data.season);
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
        if (!selectedModel || !selectedSeason) return;

        setButtonActive(true);
        try {
            const response = await fetch(`/api/nba/model/train/${selectedModel}/${selectedSeason}`);
            const data = await response.json();
            setResult(data);
        } finally {
            setButtonActive(false);
        }
    };

    const handleSearchParamsChange = (key: string, value: string | null) => {
        setSearchParams(prev => {
            if (value) prev.set(key, value);
            else prev.delete(key);
            return prev;
        });
    }

    const tabTypes = [
        { value: 'standings', label: 'Standings' },
        { value: 'predictions', label: 'Predictions' },
    ];

    return <>
        <div style={{ display: 'flex', alignItems: 'flex-end', gap: "16px", width: "100%", padding: "10px", marginBottom: '30px' }}>
            <Select
                style={{ flex: 1 }}
                label="Season"
                placeholder="Pick a Season"
                data={seasonOptions}
                value={selectedSeason}
                onChange={(value) => handleSearchParamsChange('season', value)}
                searchable
            />
            <Select
                style={{ flex: 1 }}
                label="ML Model"
                placeholder="Pick a Model"
                data={modelOptions}
                value={selectedModel}
                onChange={(value) => handleSearchParamsChange('model', value)}
                searchable
            />
            <Button
                variant="filled"
                onClick={handleRunModel}
                loading={buttonActive}
                disabled={!selectedModel || !selectedSeason}
            >
                Run Model
            </Button>
        </div>

        {result && !result.success && (
            <Text c="var(--lose)">{result.error}</Text> // change message
        )}

        {result && result.success && (
            <>
                {result.metrics && (
                    <SimpleGrid cols={4} mb="30px">
                        <StatTile label="Accuracy" value={`${(result.metrics.accuracy * 100).toFixed(1)}%`} />
                        <StatTile label="AUC" value={result.metrics.auc.toFixed(3)} />
                        <StatTile label="Log loss" value={result.metrics.log_loss.toFixed(3)} />
                        <StatTile label="Brier" value={result.metrics.brier.toFixed(3)} />
                    </SimpleGrid>
                )}

                <Tabs variant="pills" style={{ width: "100%", marginBottom: '30px' }} value={props.activeTab}>
                    <Tabs.List grow={true} style={{ width: "100%", display: 'flex', justifyContent: 'space-between' }}>
                        {tabTypes.map(type =>
                            <Tabs.Tab
                                key={type.value}
                                onClick={() => props.setActiveTab(type.value)}
                                value={type.value}
                                style={{ fontWeight: 700, fontSize: '16px' }}
                            >
                                {type.label}
                            </Tabs.Tab>
                        )}
                    </Tabs.List>
                </Tabs>

                {props.activeTab === 'standings' && result.season_records && result.season_records.length > 0 && (
                    <StandingsTable records={result.season_records} />
                )}

                {props.activeTab === 'predictions' && result.predictions && result.predictions.length > 0 && (
                    <PredictionsTable records={result.predictions} />
                )}
            </>
        )}
    </>


}
