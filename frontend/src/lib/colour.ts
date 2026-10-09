/** Percentile band that gets no fill at all, and the alpha ramp either side of it. */
const NEUTRAL_LOW = 0.425;
const NEUTRAL_HIGH = 0.575;
const MIN_ALPHA = 0.08;
const MAX_ALPHA = 0.5;

/** Channels of --hot / --cold in index.css, split out so a shade can carry an alpha. */
const HOT_RGB = '232, 98, 44';
const COLD_RGB = '62, 142, 222';

/** --ink and --paper, the only two text colours a chip ever uses. */
const INK_HEX = '#0b1013';
const PAPER_HEX = '#edeae1';

/** Two team colours closer than this read as one colour side by side. */
export const CLASH_DISTANCE = 45;

export type DivergingSide = 'up' | 'down';

export interface PercentileOptions {
    /** TOV, DRtg, losses: invert first, so a hot shade always means good. */
    lowerIsBetter?: boolean;
}

function clamp01(n: number): number {
    return Math.min(1, Math.max(0, n));
}

function parseHex(hex: string): [number, number, number] | null {
    const raw = hex.trim().replace(/^#/, '');
    const full = raw.length === 3 ? raw.replace(/./g, c => c + c) : raw;
    if (!/^[0-9a-fA-F]{6}$/.test(full)) return null;
    return [
        parseInt(full.slice(0, 2), 16),
        parseInt(full.slice(2, 4), 16),
        parseInt(full.slice(4, 6), 16),
    ];
}

function relativeLuminance([r, g, b]: [number, number, number]): number {
    const channel = (c: number) => {
        const s = c / 255;
        return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
    };
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b);
}

/**
 * Where `value` sits in `population`, 0..1. Pass the full qualified league for the
 * season, not just the rows on screen, or every table shades its own top row orange.
 */
export function percentile(
    value: number,
    population: readonly number[],
    { lowerIsBetter = false }: PercentileOptions = {},
): number {
    const values = population.filter(v => Number.isFinite(v));
    if (!Number.isFinite(value) || values.length < 2) return 0.5;

    let below = 0;
    let equal = 0;
    for (const v of values) {
        if (v < value) below += 1;
        else if (v === value) equal += 1;
    }

    // Midpoint of a tie block, so a stat where 40 players share a value doesn't put
    // all of them at the top of it.
    const p = (below + equal / 2) / values.length;
    return lowerIsBetter ? 1 - p : p;
}

/** Cell background for a percentile: transparent through the middle of the league. */
export function shade(p: number): string {
    if (!Number.isFinite(p) || (p >= NEUTRAL_LOW && p <= NEUTRAL_HIGH)) return 'transparent';

    const hot = p > NEUTRAL_HIGH;
    const distance = hot
        ? (p - NEUTRAL_HIGH) / (1 - NEUTRAL_HIGH)
        : (NEUTRAL_LOW - p) / NEUTRAL_LOW;
    const alpha = MIN_ALPHA + clamp01(distance) * (MAX_ALPHA - MIN_ALPHA);

    return `rgba(${hot ? HOT_RGB : COLD_RGB}, ${alpha.toFixed(3)})`;
}

/** Splits a signed value into a direction and a bar width against a fixed scale. */
export function diverging(delta: number, maxAbs: number): { side: DivergingSide; widthPct: number } {
    const side: DivergingSide = delta < 0 ? 'down' : 'up';
    if (!Number.isFinite(delta) || !Number.isFinite(maxAbs) || maxAbs <= 0) {
        return { side, widthPct: 0 };
    }
    return { side, widthPct: Math.min(100, (Math.abs(delta) / maxAbs) * 100) };
}

export function divergingColour(side: DivergingSide): string {
    return side === 'up' ? 'var(--hot)' : 'var(--cold)';
}

export function rgbDistance(a: string, b: string): number {
    const x = parseHex(a);
    const y = parseHex(b);
    // A colour we can't read can't be shown to clash, so leave the pair alone.
    if (!x || !y) return Infinity;
    return Math.hypot(x[0] - y[0], x[1] - y[1], x[2] - y[2]);
}

function luminanceOf(hex: string): number {
    const rgb = parseHex(hex);
    return rgb ? relativeLuminance(rgb) : 0;
}

function contrast(a: number, b: number): number {
    const [hi, lo] = a > b ? [a, b] : [b, a];
    return (hi + 0.05) / (lo + 0.05);
}

const INK_LUMINANCE = luminanceOf(INK_HEX);
const PAPER_LUMINANCE = luminanceOf(PAPER_HEX);

/**
 * Readable text colour to sit on `hex`. Picks the better of --ink and --paper rather
 * than cutting at luminance 0.5: those two cross over at 0.166, and a 0.5 cut puts pale
 * text on mid-bright colours like Minnesota's green at 1.9:1.
 */
export function chipText(hex: string): string {
    const rgb = parseHex(hex);
    if (!rgb) return 'var(--paper)';

    const luminance = relativeLuminance(rgb);
    return contrast(luminance, INK_LUMINANCE) >= contrast(luminance, PAPER_LUMINANCE)
        ? 'var(--ink)'
        : 'var(--paper)';
}
