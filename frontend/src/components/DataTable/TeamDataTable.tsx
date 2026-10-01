import { DataTable, type DataTableSortStatus } from 'mantine-datatable';
import { useMemo, useState } from 'react';
import sortBy from 'lodash/sortBy';
import 'mantine-datatable/styles.layer.css';
import type { SeasonTeamStats } from '../../types/team';
import { cellStyle, nameCellStyle, statColumns, tableProps } from './tableTheme';

export default function TeamDataTable({ teamData = [] }: { teamData: SeasonTeamStats[] }) {
    const [sortStatus, setSortStatus] = useState<DataTableSortStatus<SeasonTeamStats>>({
        columnAccessor: 'wins',
        direction: 'desc',
    });

    const records = useMemo(() => {
        const data = sortBy(teamData, sortStatus.columnAccessor);
        return sortStatus.direction === 'desc' ? data.reverse() : data;
    }, [teamData, sortStatus]);

    return (
        <DataTable<SeasonTeamStats>
            {...tableProps}
            idAccessor="team_id"
            // The name stays put while the stat columns scroll sideways.
            pinFirstColumn
            records={records}
            emptyState={null}
            sortStatus={sortStatus}
            onSortStatusChange={setSortStatus}
            columns={[
                { accessor: 'team_name', title: 'Team', sortable: true, width: 200, cellsStyle: () => nameCellStyle },
                {
                    accessor: 'wins', title: 'W', sortable: true, width: 62, textAlign: 'right',
                    cellsStyle: () => ({ ...cellStyle, color: 'var(--win)' }),
                },
                {
                    accessor: 'losses', title: 'L', sortable: true, width: 62, textAlign: 'right',
                    cellsStyle: () => ({ ...cellStyle, color: 'var(--lose)' }),
                },
                ...statColumns<SeasonTeamStats>(),
            ]}
        />
    );
}
