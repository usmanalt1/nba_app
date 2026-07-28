import { useMemo, useState } from 'react';
import { DataTable, type DataTableSortStatus } from 'mantine-datatable';
import sortBy from 'lodash/sortBy';
import type { SeasonRecord } from '../../types/predictions';

export function StandingsTable({ records }: { records: SeasonRecord[] }) {
    const [sortStatus, setSortStatus] = useState<DataTableSortStatus<SeasonRecord>>({
        columnAccessor: 'wins',
        direction: 'desc',
    });

    const sorted = useMemo(() => {
        const data = sortBy(records, sortStatus.columnAccessor);
        return sortStatus.direction === 'desc' ? data.reverse() : data;
    }, [records, sortStatus]);

    return (
        <div style={{ marginTop: '10px', width: '100%', border: '1px solid var(--mantine-color-blue-4)', borderRadius: 'var(--mantine-radius-md)', padding: '1px' }}>
            <DataTable<SeasonRecord>
                idAccessor="team"
                withTableBorder
                withColumnBorders
                records={sorted}
                emptyState={null}
                columns={[
                    { accessor: 'team', width: '40%', sortable: true },
                    { accessor: 'wins', width: '30%', sortable: true, textAlign: 'right' },
                    { accessor: 'loss', width: '30%', sortable: true, textAlign: 'right' },
                ]}
                sortStatus={sortStatus}
                onSortStatusChange={setSortStatus}
            />
        </div>
    );
}
