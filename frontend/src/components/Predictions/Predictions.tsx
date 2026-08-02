import { useEffect, useState } from 'react';
import { Select, Button, SimpleGrid, Text, Tabs } from "@mantine/core";
import 'mantine-datatable/styles.layer.css';
import { StatTile } from './StatTile';
import { StandingsTable } from './StandingsTable';
import { PredictionsTable } from './PredictionsTable';
import type { PredictionsProps } from '../../types/predictions';

export function Predictions(props: PredictionsProps) {

    const [models, setModels] = useState<{ model_name: string }[]>([]);
    const [seasons, setSeasons] = useState([]);
    const [buttonActive, setButtonActive] = useState(false);

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
        if (!props.selectedModel || !props.selectedSeason) return;

        setButtonActive(true);
        try {
            const response = await fetch(`/api/nba/model/train/${props.selectedModel}/${props.selectedSeason}`);
            const data = await response.json();
            props.setResult(data);
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
                value={props.selectedSeason}
                onChange={props.setSelectedSeason}
                searchable
            />
            <Select
                style={{ flex: 1 }}
                label="ML Model"
                placeholder="Pick a Model"
                data={modelOptions}
                value={props.selectedModel}
                onChange={props.setSelectedModel}
                searchable
            />
            <Button
                variant="filled"
                onClick={handleRunModel}
                loading={buttonActive}
                disabled={!props.selectedModel || !props.selectedSeason}
            >
                Run Model
            </Button>
        </div>

        {props.result && !props.result.success && (
            <Text c="red">{props.result.error}</Text> // change message
        )}

        {props.result && props.result.success && (
            <>
                {props.result.metrics && (
                    <SimpleGrid cols={4} mb="30px">
                        <StatTile label="Accuracy" value={`${(props.result.metrics.accuracy * 100).toFixed(1)}%`} />
                        <StatTile label="AUC" value={props.result.metrics.auc.toFixed(3)} />
                        <StatTile label="Log loss" value={props.result.metrics.log_loss.toFixed(3)} />
                        <StatTile label="Brier" value={props.result.metrics.brier.toFixed(3)} />
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

                {props.activeTab === 'standings' && props.result.season_records && props.result.season_records.length > 0 && (
                    <StandingsTable records={props.result.season_records} />
                )}

                {props.activeTab === 'predictions' && props.result.predictions && props.result.predictions.length > 0 && (
                    <PredictionsTable records={props.result.predictions} />
                )}
            </>
        )}
    </>


}
