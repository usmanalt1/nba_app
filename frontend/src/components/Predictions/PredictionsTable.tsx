import { useMemo, useState } from 'react';
import { Text } from "@mantine/core";
import { DataTable, type DataTableSortStatus } from 'mantine-datatable';
import sortBy from 'lodash/sortBy';
import type { Prediction } from './types';

export function PredictionsTable({ records }: { records: Prediction[] }) {
    const [sortStatus, setSortStatus] = useState<DataTableSortStatus<Prediction>>({
        columnAccessor: 'game_date',
        direction: 'desc',
    });

    const sorted = useMemo(() => {
        const data = sortBy(records, sortStatus.columnAccessor);
        return sortStatus.direction === 'desc' ? data.reverse() : data;
    }, [records, sortStatus]);

    return (
        <div style={{ marginTop: '10px', width: '100%', border: '1px solid var(--mantine-color-blue-4)', borderRadius: 'var(--mantine-radius-md)', padding: '1px' }}>
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
                    {
                        accessor: 'home_win_probability', title: 'Home win probability', width: '25%', sortable: true, textAlign: 'right',
                        render: (row) => `${(row.home_win_probability * 100).toFixed(1)}%`,
                    },
                    {
                        accessor: 'result', title: 'Result', width: '25%', textAlign: 'right',
                        render: (row) => {
                            const correct = row.predicted_home_win === row.actual_home_win;
                            return (
                                <Text c={correct ? 'teal' : 'red'} fw={600}>
                                    {correct ? 'Correct' : 'Miss'}
                                </Text>
                            );
                        },
                    },
                ]}
                sortStatus={sortStatus}
                onSortStatusChange={setSortStatus}
            />
        </div>
    );
}
