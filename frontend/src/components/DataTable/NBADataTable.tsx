import { DataTable, type DataTableSortStatus } from 'mantine-datatable';
import { useMemo, useState } from 'react';
import sortBy from 'lodash/sortBy';
import 'mantine-datatable/styles.layer.css';
import type { SeasonPlayerStats } from '../../types/player';
import { average, cellStyle, nameCellStyle, signed, signedCellStyle, tableProps } from './tableTheme';

export default function NBADataTable({ nbaData = [] }: { nbaData: SeasonPlayerStats[] }) {
    const [sortStatus, setSortStatus] = useState<DataTableSortStatus<SeasonPlayerStats>>({
        columnAccessor: 'average_points',
        direction: 'desc',
    });

    const records = useMemo(() => {
        const data = sortBy(nbaData, sortStatus.columnAccessor);
        return sortStatus.direction === 'desc' ? data.reverse() : data;
    }, [nbaData, sortStatus]);

    return (
        <DataTable<SeasonPlayerStats>
            {...tableProps}
            idAccessor="player_id"
            records={records}
            emptyState={null}
            sortStatus={sortStatus}
            onSortStatusChange={setSortStatus}
            columns={[
                { accessor: 'player_name', title: 'Player', sortable: true, width: '30%', cellsStyle: () => nameCellStyle },
                {
                    accessor: 'position', title: 'Pos', sortable: true, width: '10%',
                    cellsStyle: () => ({ ...cellStyle, color: 'var(--paper-faint)' }),
                    render: ({ position }) => position ?? '—',
                },
                { accessor: 'games_played', title: 'GP', sortable: true, width: '10%', textAlign: 'right', cellsStyle: () => cellStyle },
                {
                    accessor: 'average_points', title: 'PTS', sortable: true, width: '12%', textAlign: 'right',
                    cellsStyle: () => ({ ...cellStyle, color: 'var(--paper)' }),
                    render: ({ average_points }) => average(average_points),
                },
                {
                    accessor: 'average_rebounds', title: 'REB', sortable: true, width: '12%', textAlign: 'right',
                    cellsStyle: () => cellStyle,
                    render: ({ average_rebounds }) => average(average_rebounds),
                },
                {
                    accessor: 'average_assists', title: 'AST', sortable: true, width: '12%', textAlign: 'right',
                    cellsStyle: () => cellStyle,
                    render: ({ average_assists }) => average(average_assists),
                },
                {
                    accessor: 'average_plus_minus', title: '+/-', sortable: true, width: '14%', textAlign: 'right',
                    cellsStyle: ({ average_plus_minus: pm }) => signedCellStyle(pm),
                    render: ({ average_plus_minus: pm }) => signed(pm),
                },
            ]}
        />
    );
}
