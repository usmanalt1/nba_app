import type { DataTableColumn } from 'mantine-datatable';
import type { BoxScoreAverages } from '../../types/stats';

// Shared look for the data tables: mono/uppercase headers in the same register as
// the filter pills, tabular digits so decimals line up, and the app's dark palette.
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

/** The identifying first column: brighter and bolder than the stat columns. */
export const nameCellStyle = { ...cellStyle, color: 'var(--paper)', fontWeight: 700 };

/** Sign carries the meaning for +/-, so it gets the win/lose accents. */
export const signedCellStyle = (value: number | null) => ({
    ...cellStyle,
    color: value === null ? 'var(--paper-faint)'
        : value > 0 ? 'var(--win)' : value < 0 ? 'var(--lose)' : 'var(--paper-faint)',
});

/** One decimal is the NBA convention for per-game averages; null means no data. */
export const average = (value: number | null) => (value === null ? '—' : value.toFixed(1));

/** Averages read better with an explicit + when positive. */
export const signed = (value: number | null) =>
    value === null ? '—' : value > 0 ? `+${average(value)}` : average(value);

/** Percentages are already 0-100 from the API. */
export const percent = (value: number | null) => (value === null ? '—' : `${value.toFixed(1)}%`);

/** Colour and spacing props shared by every DataTable on the page. */
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

/** Fixed width per stat column: the table scrolls sideways rather than squashing. */
const STAT_WIDTH = 78;

type StatSpec = { accessor: keyof BoxScoreAverages; title: string; kind?: 'plain' | 'percent' | 'signed' };

// Standard box-score reading order.
const STAT_SPECS: StatSpec[] = [
    { accessor: 'games_played', title: 'GP', kind: 'plain' },
    { accessor: 'average_minutes', title: 'MIN' },
    { accessor: 'average_points', title: 'PTS' },
    { accessor: 'average_field_goals_made', title: 'FGM' },
    { accessor: 'average_field_goals_attempted', title: 'FGA' },
    { accessor: 'field_goal_pct', title: 'FG%', kind: 'percent' },
    { accessor: 'average_three_pointers_made', title: '3PM' },
    { accessor: 'average_three_pointers_attempted', title: '3PA' },
    { accessor: 'three_point_pct', title: '3P%', kind: 'percent' },
    { accessor: 'average_free_throws_made', title: 'FTM' },
    { accessor: 'average_free_throws_attempted', title: 'FTA' },
    { accessor: 'free_throw_pct', title: 'FT%', kind: 'percent' },
    { accessor: 'average_offensive_rebounds', title: 'OREB' },
    { accessor: 'average_defensive_rebounds', title: 'DREB' },
    { accessor: 'average_rebounds', title: 'REB' },
    { accessor: 'average_assists', title: 'AST' },
    { accessor: 'average_steals', title: 'STL' },
    { accessor: 'average_blocks', title: 'BLK' },
    { accessor: 'average_turnovers', title: 'TOV' },
    { accessor: 'average_fouls', title: 'PF' },
    { accessor: 'average_plus_minus', title: '+/-', kind: 'signed' },
];

/**
 * The box-score stat columns, identical for players and teams. Both tables build
 * from this list so a column added here shows up in both.
 */
export function statColumns<T extends BoxScoreAverages>(): DataTableColumn<T>[] {
    return STAT_SPECS.map(({ accessor, title, kind = 'plain' }) => ({
        accessor,
        title,
        sortable: true,
        width: STAT_WIDTH,
        textAlign: 'right' as const,
        cellsStyle: (record: T) =>
            kind === 'signed' ? signedCellStyle(record[accessor] as number | null) : cellStyle,
        render: (record: T) => {
            const value = record[accessor] as number | null;
            if (kind === 'percent') return percent(value);
            if (kind === 'signed') return signed(value);
            // Games played is a whole number; the rest are averages.
            return accessor === 'games_played' ? String(value ?? '—') : average(value);
        },
    }));
}
