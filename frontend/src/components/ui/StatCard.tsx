import type { ReactNode } from 'react';

interface StatCardProps {
    label: string;
    value: string;
    /** Sits under the value: context, a denominator, a comparison. */
    note?: ReactNode;
    /** Tints the value. Use sparingly — one hero number per row at most. */
    tone?: 'default' | 'brand' | 'win' | 'lose';
    /** Hero sizing for the single number a section leads with. */
    hero?: boolean;
}

const TONE_COLOR: Record<NonNullable<StatCardProps['tone']>, string> = {
    default: 'var(--paper)',
    brand: 'var(--worm)',
    win: 'var(--win)',
    lose: 'var(--lose)',
};

export function StatCard({ label, value, note, tone = 'default', hero = false }: StatCardProps) {
    return (
        <div
            style={{
                border: '1px solid var(--line)',
                background: 'var(--panel)',
                borderRadius: 4,
                padding: hero ? '18px 20px' : '14px 16px',
                minWidth: 0,
            }}
        >
            <div className="kicker" style={{ marginBottom: 8 }}>{label}</div>
            <div
                style={{
                    fontFamily: "'Oswald', sans-serif",
                    fontSize: hero ? 42 : 28,
                    fontWeight: 600,
                    lineHeight: 1,
                    letterSpacing: '-0.01em',
                    color: TONE_COLOR[tone],
                    fontVariantNumeric: 'tabular-nums',
                }}
            >
                {value}
            </div>
            {note && (
                <div style={{ fontSize: 12, color: 'var(--paper-dim)', marginTop: 8, lineHeight: 1.35 }}>
                    {note}
                </div>
            )}
        </div>
    );
}
