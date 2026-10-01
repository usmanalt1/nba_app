import { DataTable, type DataTableSortStatus } from 'mantine-datatable';
import { useMemo, useState } from 'react';
import sortBy from 'lodash/sortBy';
import 'mantine-datatable/styles.layer.css';
import type { SeasonTeamStats } from '../../types/team';
import { average, cellStyle, nameCellStyle, signed, signedCellStyle, tableProps } from './tableTheme';

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
            records={records}
            emptyState={null}
            sortStatus={sortStatus}
            onSortStatusChange={setSortStatus}
            columns={[
                { accessor: 'team_name', title: 'Team', sortable: true, width: '28%', cellsStyle: () => nameCellStyle },
                { accessor: 'games_played', title: 'GP', sortable: true, width: '9%', textAlign: 'right', cellsStyle: () => cellStyle },
                {
                    accessor: 'wins', title: 'W', sortable: true, width: '9%', textAlign: 'right',
                    cellsStyle: () => ({ ...cellStyle, color: 'var(--win)' }),
                },
                {
                    accessor: 'losses', title: 'L', sortable: true, width: '9%', textAlign: 'right',
                    cellsStyle: () => ({ ...cellStyle, color: 'var(--lose)' }),
                },
                {
                    accessor: 'average_points', title: 'PTS', sortable: true, width: '11%', textAlign: 'right',
                    cellsStyle: () => ({ ...cellStyle, color: 'var(--paper)' }),
                    render: ({ average_points }) => average(average_points),
                },
                {
                    accessor: 'average_rebounds', title: 'REB', sortable: true, width: '11%', textAlign: 'right',
                    cellsStyle: () => cellStyle,
                    render: ({ average_rebounds }) => average(average_rebounds),
                },
                {
                    accessor: 'average_assists', title: 'AST', sortable: true, width: '11%', textAlign: 'right',
                    cellsStyle: () => cellStyle,
                    render: ({ average_assists }) => average(average_assists),
                },
                {
                    accessor: 'average_plus_minus', title: '+/-', sortable: true, width: '12%', textAlign: 'right',
                    cellsStyle: ({ average_plus_minus: pm }) => signedCellStyle(pm),
                    render: ({ average_plus_minus: pm }) => signed(pm),
                },
            ]}
        />
    );
}
