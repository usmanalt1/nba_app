import { useMemo, useState } from 'react';
import { DataTable, type DataTableSortStatus } from 'mantine-datatable';
import sortBy from 'lodash/sortBy';
import type { SeasonRecord } from '../../types/predictions';
import { cellStyle, header, nameCellStyle, tableProps } from '../DataTable/tableTheme';

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
        <div style={{ width: '100%', height: 600 }}>
            <DataTable<SeasonRecord>
                {...tableProps}
                idAccessor="team"
                records={sorted}
                emptyState={null}
                columns={[
                    { accessor: 'team', title: header('Team', 'Team name'), width: '40%', sortable: true, cellsStyle: () => nameCellStyle },
                    { accessor: 'wins', title: header('W', 'Wins'), width: '30%', sortable: true, textAlign: 'right', cellsStyle: () => cellStyle },
                    { accessor: 'loss', title: header('L', 'Losses'), width: '30%', sortable: true, textAlign: 'right', cellsStyle: () => cellStyle },
                ]}
                sortStatus={sortStatus}
                onSortStatusChange={setSortStatus}
            />
        </div>
    );
}
