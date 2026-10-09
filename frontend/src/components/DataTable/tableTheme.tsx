import { Tooltip } from '@mantine/core';
import type { DataTableColumn } from 'mantine-datatable';
import type { AdvancedAverages, BoxScoreAverages } from '../../types/stats';

export const headerStyle = {
    backgroundColor: 'var(--panel-2)',
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: '12px',
    fontWeight: 700,
    textTransform: 'uppercase' as const,
    letterSpacing: '0.08em',
    color: 'var(--paper-faint)',
};

export const cellStyle = {
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: '14px',
    color: 'var(--paper-dim)',
    fontVariantNumeric: 'tabular-nums' as const,
};

export const nameCellStyle = { ...cellStyle, color: 'var(--paper)', fontWeight: 700 };

export const signedCellStyle = (value: number | null) => ({
    ...cellStyle,
    color: value === null ? 'var(--paper-faint)'
        : value > 0 ? 'var(--win)' : value < 0 ? 'var(--lose)' : 'var(--paper-faint)',
});

export const average = (value: number | null) => (value === null ? '—' : value.toFixed(1));

export const signed = (value: number | null) =>
    value === null ? '—' : value > 0 ? `+${average(value)}` : average(value);

// Already 0-100 from the API.
export const percent = (value: number | null) => (value === null ? '—' : `${value.toFixed(1)}%`);

export const tableProps = {
    withTableBorder: true,
    striped: true,
    highlightOnHover: true,
    borderRadius: 'sm',
    verticalSpacing: 'xs',
    horizontalSpacing: 'md',
    backgroundColor: 'var(--court)',
    borderColor: 'var(--line)',
    rowBorderColor: 'var(--line)',
    stripedColor: 'var(--panel)',
    highlightOnHoverColor: 'var(--panel-2)',
    styles: { header: headerStyle },
} as const;


// The span gives Tooltip an element to attach to, keeping the header itself sortable.
export function header(label: string, description: string) {
    return (
        <Tooltip label={description} withArrow openDelay={200} position="top">
            <span style={{ cursor: 'help' }}>{label}</span>
        </Tooltip>
    );
}

// Fixed, so the table scrolls sideways rather than squashing the columns.
const STAT_WIDTH = 78;

type StatSpec = { description: string; accessor: keyof BoxScoreAverages; title: string; kind?: 'plain' | 'percent' | 'signed' };

// Standard box-score reading order.
const STAT_SPECS: StatSpec[] = [
    { accessor: 'games_played', title: 'GP', kind: 'plain', description: 'Games played' },
    { accessor: 'average_minutes', title: 'MIN', description: 'Minutes per game' },
    { accessor: 'average_points', title: 'PTS', description: 'Points per game' },
    { accessor: 'average_field_goals_made', title: 'FGM', description: 'Field goals made per game' },
    { accessor: 'average_field_goals_attempted', title: 'FGA', description: 'Field goals attempted per game' },
    { accessor: 'field_goal_pct', title: 'FG%', kind: 'percent', description: 'Field goal percentage, from season totals' },
    { accessor: 'average_three_pointers_made', title: '3PM', description: 'Three pointers made per game' },
    { accessor: 'average_three_pointers_attempted', title: '3PA', description: 'Three pointers attempted per game' },
    { accessor: 'three_point_pct', title: '3P%', kind: 'percent', description: 'Three point percentage, from season totals' },
    { accessor: 'average_free_throws_made', title: 'FTM', description: 'Free throws made per game' },
    { accessor: 'average_free_throws_attempted', title: 'FTA', description: 'Free throws attempted per game' },
    { accessor: 'free_throw_pct', title: 'FT%', kind: 'percent', description: 'Free throw percentage, from season totals' },
    { accessor: 'average_offensive_rebounds', title: 'OREB', description: 'Offensive rebounds per game' },
    { accessor: 'average_defensive_rebounds', title: 'DREB', description: 'Defensive rebounds per game' },
    { accessor: 'average_rebounds', title: 'REB', description: 'Total rebounds per game' },
    { accessor: 'average_assists', title: 'AST', description: 'Assists per game' },
    { accessor: 'average_steals', title: 'STL', description: 'Steals per game' },
    { accessor: 'average_blocks', title: 'BLK', description: 'Blocks per game' },
    { accessor: 'average_turnovers', title: 'TOV', description: 'Turnovers per game' },
    { accessor: 'average_fouls', title: 'PF', description: 'Personal fouls per game' },
    { accessor: 'average_plus_minus', title: '+/-', kind: 'signed', description: 'Plus/minus: average scoring margin while on court' },
];

export function statColumns<T extends BoxScoreAverages>(): DataTableColumn<T>[] {
    return STAT_SPECS.map(({ accessor, title, description, kind = 'plain' }) => ({
        accessor,
        title: header(title, description),
        sortable: true,
        width: STAT_WIDTH,
        textAlign: 'right' as const,
        cellsStyle: (record: T) =>
            kind === 'signed' ? signedCellStyle(record[accessor] as number | null) : cellStyle,
        render: (record: T) => {
            const value = record[accessor] as number | null;
            if (kind === 'percent') return percent(value);
            if (kind === 'signed') return signed(value);
            return accessor === 'games_played' ? String(value ?? '—') : average(value);
        },
    }));
}

type AdvancedSpec = { description: string; accessor: keyof AdvancedAverages; title: string; kind?: 'plain' | 'percent' | 'signed' };

// Record and minutes, then the ratings, then efficiency and usage shares.
const ADVANCED_SPECS: AdvancedSpec[] = [
    { accessor: 'games_played', title: 'GP', kind: 'plain', description: 'Games played' },
    { accessor: 'wins', title: 'W', kind: 'plain', description: 'Wins' },
    { accessor: 'losses', title: 'L', kind: 'plain', description: 'Losses' },
    { accessor: 'average_minutes', title: 'MIN', description: 'Minutes per game' },
    { accessor: 'offensive_rating', title: 'ORTG', description: 'Offensive rating: points scored per 100 possessions' },
    { accessor: 'defensive_rating', title: 'DRTG', description: 'Defensive rating: points allowed per 100 possessions' },
    { accessor: 'net_rating', title: 'NETRTG', kind: 'signed', description: 'Net rating: offensive minus defensive rating' },
    { accessor: 'true_shooting_percentage', title: 'TS%', kind: 'percent', description: 'True shooting %: efficiency counting free throws and threes' },
    { accessor: 'effective_field_goal_percentage', title: 'EFG%', kind: 'percent', description: 'Effective field goal %: field goal % weighting threes' },
    { accessor: 'usage_percentage', title: 'USG%', kind: 'percent', description: 'Usage %: share of team possessions used' },
    { accessor: 'assist_percentage', title: 'AST%', kind: 'percent', description: 'Assist %: share of teammate field goals assisted' },
    { accessor: 'assist_ratio', title: 'AST RT', description: 'Assist ratio: assists per 100 possessions used' },
    { accessor: 'assist_to_turnover', title: 'AST/TO', description: 'Assists per turnover' },
    { accessor: 'turnover_percentage', title: 'TOV%', kind: 'percent', description: 'Turnover %: turnovers per 100 possessions' },
    { accessor: 'offensive_rebound_percentage', title: 'OREB%', kind: 'percent', description: 'Offensive rebound %: share of available offensive rebounds' },
    { accessor: 'defensive_rebound_percentage', title: 'DREB%', kind: 'percent', description: 'Defensive rebound %: share of available defensive rebounds' },
    { accessor: 'rebound_percentage', title: 'REB%', kind: 'percent', description: 'Rebound %: share of all available rebounds' },
    { accessor: 'pace', title: 'PACE', description: 'Pace: possessions per 48 minutes' },
    { accessor: 'possessions', title: 'POSS', description: 'Possessions per game' },
    { accessor: 'pie', title: 'PIE', kind: 'percent', description: 'Player impact estimate: share of game events contributed' },
];

export function advancedColumns<T extends AdvancedAverages>(): DataTableColumn<T>[] {
    return ADVANCED_SPECS.map(({ accessor, title, description, kind = 'plain' }) => ({
        accessor,
        title: header(title, description),
        sortable: true,
        width: STAT_WIDTH,
        textAlign: 'right' as const,
        cellsStyle: (record: T) =>
            kind === 'signed' ? signedCellStyle(record[accessor] as number | null) : cellStyle,
        render: (record: T) => {
            const value = record[accessor] as number | null;
            if (kind === 'percent') return percent(value);
            if (kind === 'signed') return signed(value);
            return ['games_played', 'wins', 'losses'].includes(accessor as string)
                ? String(value ?? '—')
                : average(value);
        },
    }));
}
