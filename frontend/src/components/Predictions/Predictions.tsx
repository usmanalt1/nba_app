import { useEffect, useState } from 'react';
import { Select, Button, SimpleGrid, Text, Tabs } from "@mantine/core";
import 'mantine-datatable/styles.layer.css';
import { StatTile } from './StatTile';
import { StandingsTable } from './StandingsTable';
import { PredictionsTable } from './PredictionsTable';
import type { TrainResponse } from './types';

export function Predictions() {

    const [models, setModels] = useState<{ model_name: string }[]>([]);
    const [selectedModel, setSelectedModel] = useState<string | null>(null);
    const [seasons, setSeasons] = useState([]);
    const [selectedSeason, setSelectedSeason] = useState<string | null>(null);
    const [buttonActive, setButtonActive] = useState(false);
    const [result, setResult] = useState<TrainResponse | null>(null);
    const [activeTab, setActiveTab] = useState('standings');

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
                onChange={setSelectedSeason}
                searchable
            />
            <Select
                style={{ flex: 1 }}
                label="ML Model"
                placeholder="Pick a Model"
                data={modelOptions}
                value={selectedModel}
                onChange={setSelectedModel}
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
            <Text c="red">{result.error}</Text>
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

                <Tabs variant="pills" style={{ width: "100%", marginBottom: '30px' }} value={activeTab}>
                    <Tabs.List grow={true} style={{ width: "100%", display: 'flex', justifyContent: 'space-between' }}>
                        {tabTypes.map(type =>
                            <Tabs.Tab
                                key={type.value}
                                onClick={() => setActiveTab(type.value)}
                                value={type.value}
                                style={{ fontWeight: 700, fontSize: '16px' }}
                            >
                                {type.label}
                            </Tabs.Tab>
                        )}
                    </Tabs.List>
                </Tabs>

                {activeTab === 'standings' && result.season_records && result.season_records.length > 0 && (
                    <StandingsTable records={result.season_records} />
                )}

                {activeTab === 'predictions' && result.predictions && result.predictions.length > 0 && (
                    <PredictionsTable records={result.predictions} />
                )}
            </>
        )}
    </>


}
