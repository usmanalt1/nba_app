import { useMemo, useState, useEffect } from 'react';
import { Text } from "@mantine/core";
import { DataTable, type DataTableSortStatus } from 'mantine-datatable';
import sortBy from 'lodash/sortBy';
import type { Prediction } from '../../types/predictions';
import { Select } from "@mantine/core";
import { useSearchParams } from 'react-router-dom';
import { handleSearchParams } from '../Helper/HandleSearchParams';


export function PredictionsTable({ records }: { records: Prediction[]}) {
    const [sortStatus, setSortStatus] = useState<DataTableSortStatus<Prediction>>({
        columnAccessor: 'game_date',
        direction: 'desc',
    });
    const [searchParams, setSearchParams] = useSearchParams();
    const [teamFilter, setTeamFilter] = useState([])
    const resultFilter = searchParams.get('result_filter') as 'all' | 'correct' | 'incorrect' || 'all';
    const selectedTeamParam = searchParams.get('team');

    useEffect(() => {
        fetch("/api/nba/db/list_all_teams")
            .then(r => r.json())
            .then(setTeamFilter);
    }, []);

    const teamOptions = teamFilter.map((p: any) => ({
        value: String(p.team_name),
        label: p.team_name,
    }));

    const filtered = useMemo(() => {
        return records.filter((row) => {
            if (selectedTeamParam !== null && !row.matchup.includes(selectedTeamParam)) {
                return false;
            }
            if (resultFilter === 'all') {
                return true;
            }
            const correct = row.predicted_home_win === row.actual_home_win;
            return resultFilter === 'correct' ? correct : !correct;
        });
    }, [records, resultFilter, selectedTeamParam]);


    const sorted = useMemo(() => {
        const data = sortBy(filtered, sortStatus.columnAccessor);
        return sortStatus.direction === 'desc' ? data.reverse() : data;
    }, [filtered, sortStatus]);

    const handleSearchParamsChange = (key: string, value: string | null) => {
        handleSearchParams(setSearchParams, key, value);
    }


    return (
        <div style={{ marginTop: '10px', width: '100%' }}>
            <div style={{ display: 'flex', gap: "16px", marginBottom: '16px', width: '50%' }}>
                <Select
                    style={{ flex: 10, maxWidth: '250px' }}
                    label="Result"
                    data={[
                        { value: 'all', label: 'All' },
                        { value: 'correct', label: 'Correct only' },
                        { value: 'incorrect', label: 'Incorrect only' },
                    ]}
                    value={resultFilter}
                    onChange={(v) => handleSearchParamsChange('result_filter', v)}
                />
                <Select
                    style={{ flex: 10, maxWidth: '250px' }}
                    label="Team"
                    placeholder="Pick a Team"
                    data={teamOptions}
                    value={selectedTeamParam}
                    onChange={(v) => handleSearchParamsChange('team', v)}
                    searchable
                />
            </div>
            <div style={{ width: '100%', border: '1px solid var(--line)', borderRadius: 4, padding: '1px', marginBottom: '30px', fontFamily: "'IBM Plex Mono', monospace" }}>
            <DataTable<Prediction>
                idAccessor="game_id"
                withTableBorder
                withColumnBorders
                records={sorted}
                emptyState={null}
                columns={[
                    {
                        accessor: 'game_date', title: 'Date', width: '15%', sortable: true,
                        render: (row) => new Date(row.game_date).toLocaleDateString(),
                    },
                    { accessor: 'matchup', width: '35%', sortable: true },
                    { accessor: 'home_team_name', width: '10%', sortable: true },
                    {
                        accessor: 'home_win_probability', title: 'Home win probability', width: '10%', sortable: true, textAlign: 'left',
                        render: (row) => `${(row.home_win_probability * 100).toFixed(1)}%`,
                    },
                    {
                        accessor: 'result', title: 'Result', width: '10%', textAlign: 'left',
                        render: (row) => {
                            const correct = row.predicted_home_win === row.actual_home_win;
                            return (
                                <Text c={correct ? 'var(--win)' : 'var(--lose)'} fw={600}>
                                    {correct ? 'Correct' : 'Incorrect'}
                                </Text>
                            );
                        },
                    },
                ]}
                sortStatus={sortStatus}
                onSortStatusChange={setSortStatus}
            />
            </div>
        </div>
    );
}
