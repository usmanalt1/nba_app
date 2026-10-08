import { useMemo, useState, useEffect } from 'react';
import { DataTable, type DataTableSortStatus } from 'mantine-datatable';
import { cellStyle, header, nameCellStyle, tableProps } from '../DataTable/tableTheme';
import sortBy from 'lodash/sortBy';
import type { Prediction } from '../../types/predictions';
import { Select } from "@mantine/core";
import { useSearchParams } from 'react-router-dom';
import { handleSearchParams } from '../Helper/HandleSearchParams';
import { apiFetch } from '../../lib/api';


export function PredictionsTable({ records }: { records: Prediction[]}) {
    const [sortStatus, setSortStatus] = useState<DataTableSortStatus<Prediction>>({
        columnAccessor: 'game_date',
        direction: 'desc',
    });
    const [searchParams, setSearchParams] = useSearchParams();
    const [teamFilter, setTeamFilter] = useState([])
    const resultFilter = searchParams.get('result_filter') as 'all' | 'correct' | 'incorrect' | 'pending' || 'all';
    const selectedTeamParam = searchParams.get('team');

    useEffect(() => {
        apiFetch("/api/nba/db/list_all_teams")
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
            // unplayed: neither correct nor incorrect
            if (typeof row.actual_home_win !== 'boolean') {
                return resultFilter === 'pending';
            }
            if (resultFilter === 'pending') {
                return false;
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
            <div style={{ display: 'flex', gap: "16px", marginBottom: '16px', width: '50%'}}>
                <Select
                    style={{ flex: 10, maxWidth: '250px' }}
                    label="Result"
                    data={[
                        { value: 'all', label: 'All' },
                        { value: 'correct', label: 'Correct only' },
                        { value: 'incorrect', label: 'Incorrect only' },
                        { value: 'pending', label: 'Not yet played' },
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
            <div style={{ width: '100%', height: 500 }}>
            <DataTable<Prediction>
                {...tableProps}
                idAccessor="game_id"
                records={sorted}
                emptyState={null}
                columns={[
                    {
                        accessor: 'game_date', title: header('Date', 'Date the game was played'), width: '15%', sortable: true,
                        cellsStyle: () => cellStyle,
                        render: (row) => new Date(row.game_date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
                    },
                    { accessor: 'matchup', title: header('Matchup', 'Home team vs away team'), width: '35%', sortable: true, cellsStyle: () => nameCellStyle },
                    { accessor: 'home_team_name', title: header('Home', 'Home team'), width: '10%', sortable: true, cellsStyle: () => cellStyle },
                    {
                        accessor: 'home_win_probability', title: header('Home win', 'Probability the model gave the home team'), width: '10%', sortable: true, textAlign: 'right',
                        cellsStyle: () => cellStyle,
                        render: (row) => `${(row.home_win_probability * 100).toFixed(1)}%`,
                    },
                    {
                        accessor: 'result', title: header('Result', 'Whether the call turned out right'), width: '10%', textAlign: 'right',
                        cellsStyle: () => cellStyle,
                        render: (row) => {
                            // Unplayed games are neither hit nor miss.
                            if (typeof row.actual_home_win !== 'boolean') {
                                return <span style={{ color: 'var(--paper-faint)' }}>—</span>;
                            }
                            const correct = row.predicted_home_win === row.actual_home_win;
                            return (
                                <span style={{ color: correct ? 'var(--win)' : 'var(--lose)', fontWeight: 700 }}>
                                    {correct ? 'Hit' : 'Miss'}
                                </span>
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
