import { DataTable, type DataTableSortStatus } from 'mantine-datatable';
import { useMemo, useState } from 'react';
import sortBy from 'lodash/sortBy';
import 'mantine-datatable/styles.layer.css';
import type { SeasonTeamStats } from '../../types/team';
import { cellStyle, header, nameCellStyle, statColumns, tableProps } from './tableTheme';

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
            pinFirstColumn
            records={records}
            emptyState={null}
            sortStatus={sortStatus}
            onSortStatusChange={setSortStatus}
            columns={[
                { accessor: 'team_name', title: header('Team', 'Team name'), sortable: true, width: 200, cellsStyle: () => nameCellStyle },
                {
                    accessor: 'wins', title: header('W', 'Wins'), sortable: true, width: 62, textAlign: 'right',
                    cellsStyle: () => ({ ...cellStyle, color: 'var(--win)' }),
                },
                {
                    accessor: 'losses', title: header('L', 'Losses'), sortable: true, width: 62, textAlign: 'right',
                    cellsStyle: () => ({ ...cellStyle, color: 'var(--lose)' }),
                },
                ...statColumns<SeasonTeamStats>(),
            ]}
        />
    );
}
