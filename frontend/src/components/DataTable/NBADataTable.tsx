import { DataTable, type DataTableSortStatus } from 'mantine-datatable';
import { useMemo, useState } from 'react';
import sortBy from 'lodash/sortBy';
import 'mantine-datatable/styles.layer.css';


interface PlayerStats {
    season: string;
    points: number;
    rebounds: number;
    plusMinus: number;
    assists: number;
}

export default function NBADataTable({ nbaData = [] }: { nbaData: PlayerStats[] }) {
    const [sortStatus, setSortStatus] = useState<DataTableSortStatus<PlayerStats>>({
        columnAccessor: 'season',
        direction: 'desc',
    });

    const records = useMemo(() => {
        const data = sortBy(nbaData, sortStatus.columnAccessor);
        return sortStatus.direction === 'desc' ? data.reverse() : data;
    }, [nbaData, sortStatus]);

    return (
    <DataTable<PlayerStats>
      idAccessor="season"
      withTableBorder
      withColumnBorders
      records={records}
      emptyState={null}
      columns={[
        { accessor: 'season', width: '20%', sortable: true },
        { accessor: 'points', width: '10%', sortable: true },
        { accessor: 'rebounds', width: '10%', sortable: true },
        { accessor: 'plusMinus', width: '15%', sortable: true, textAlign: 'right' },
        { accessor: 'assists', width: '15%', sortable: true, textAlign: 'right' },
      ]}
      sortStatus={sortStatus}
      onSortStatusChange={setSortStatus}
    />
  );
}