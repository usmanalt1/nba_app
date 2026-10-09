import { useMemo, useState } from 'react';
import { DataTable, type DataTableSortStatus } from 'mantine-datatable';
import sortBy from 'lodash/sortBy';
import { cellStyle, header, nameCellStyle, signedCellStyle, tableProps } from '../DataTable/tableTheme';
import { useSeasonTeamStats } from '../../hooks/useSeasonStats';
import type { SeasonTeamStats } from '../../types/team';

type Row = SeasonTeamStats & { win_pct: number };

const ROW_HEIGHT = 44;

interface SeasonStandingsProps {
    season: string | null;
    seasonType: string;
    /** "Regular", "Playoffs" - used in the empty state only. */
    stageLabel: string;
}

export function SeasonStandings({ season, seasonType, stageLabel }: SeasonStandingsProps) {
    const { rows, loading } = useSeasonTeamStats(season, seasonType);
    const [sortStatus, setSortStatus] = useState<DataTableSortStatus<Row>>({
        columnAccessor: 'wins',
        direction: 'desc',
    });

    const records = useMemo<Row[]>(() => {
        const withPct = rows.map((team) => ({
            ...team,
            win_pct: team.wins / Math.max(1, team.wins + team.losses),
        }));
        const sorted = sortBy(withPct, sortStatus.columnAccessor);
        return sortStatus.direction === 'desc' ? sorted.reverse() : sorted;
    }, [rows, sortStatus]);

    if (loading) {
        return <div style={{ fontSize: 13, color: 'var(--paper-faint)', padding: '8px 0' }}>Reading the table…</div>;
    }

    if (records.length === 0) {
        return (
            <div style={{ fontSize: 13, color: 'var(--paper-faint)', padding: '8px 0' }}>
                No {stageLabel.toLowerCase()} games on record for {season ?? 'this season'} yet.
            </div>
        );
    }

    return (
        // Height from the row count: a fixed one gaps on the shorter stage.
        <div style={{ width: '100%', height: Math.min(records.length, 16) * ROW_HEIGHT + 56 }}>
            <DataTable<Row>
                {...tableProps}
                idAccessor="team_id"
                records={records}
                emptyState={null}
                sortStatus={sortStatus}
                onSortStatusChange={setSortStatus}
                columns={[
                    { accessor: 'team_name', title: header('Team', 'Team name'), width: 200, sortable: true, cellsStyle: () => nameCellStyle },
                    { accessor: 'games_played', title: header('GP', 'Games played'), width: 64, sortable: true, textAlign: 'right', cellsStyle: () => cellStyle },
                    { accessor: 'wins', title: header('W', 'Wins'), width: 64, sortable: true, textAlign: 'right', cellsStyle: () => cellStyle },
                    { accessor: 'losses', title: header('L', 'Losses'), width: 64, sortable: true, textAlign: 'right', cellsStyle: () => cellStyle },
                    {
                        accessor: 'win_pct', title: header('WIN%', 'Share of games won'), width: 78, sortable: true, textAlign: 'right',
                        cellsStyle: () => cellStyle,
                        render: (team) => `${(team.win_pct * 100).toFixed(1)}%`,
                    },
                    {
                        accessor: 'average_points', title: header('PTS', 'Points per game'), width: 72, sortable: true, textAlign: 'right',
                        cellsStyle: () => cellStyle,
                        render: (team) => (team.average_points ?? 0).toFixed(1),
                    },
                    {
                        accessor: 'average_plus_minus', title: header('+/-', 'Average scoring margin'), width: 72, sortable: true, textAlign: 'right',
                        cellsStyle: (team) => signedCellStyle(team.average_plus_minus ?? null),
                        render: (team) => {
                            const margin = team.average_plus_minus ?? 0;
                            return `${margin > 0 ? '+' : ''}${margin.toFixed(1)}`;
                        },
                    },
                ]}
            />
        </div>
    );
}
