import { useEffect, useState } from 'react';
import { Select } from "@mantine/core";
import { Button } from '@mantine/core';



export function Predictions() {

    const [models, setModels] = useState<{ model_name: string }[]>([]);
    const [selectedModel, setSelectedModel] = useState<string | null>(null);
    const [seasons, setSeasons] = useState([]);
    const [selectedSeason, setSelectedSeason] = useState<string | null>(null);
    const [buttonActive, setButtonActive] = useState(false);
    const [result, setResult] = useState<any>(null);

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

    return <div style={{ display: 'flex', alignItems: 'flex-end', gap: "16px", width: "100%", padding: "10px", marginBottom: '30px' }}>
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


}