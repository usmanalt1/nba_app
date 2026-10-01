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
export const signedCellStyle = (value: number) => ({
    ...cellStyle,
    color: value > 0 ? 'var(--win)' : value < 0 ? 'var(--lose)' : 'var(--paper-faint)',
});

/** One decimal is the NBA convention for per-game averages. */
export const average = (value: number) => value.toFixed(1);

/** Averages read better with an explicit + when positive. */
export const signed = (value: number) => (value > 0 ? `+${average(value)}` : average(value));

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
