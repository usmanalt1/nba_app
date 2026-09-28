import type { ReactNode } from 'react';

interface SectionHeaderProps {
    /** Two-digit rail number that runs down the left of the page. */
    index?: string;
    title: string;
    subtitle?: string;
    /** Right-aligned meta: filters, counts, legends. */
    meta?: ReactNode;
}

export function SectionHeader({ index, title, subtitle, meta }: SectionHeaderProps) {
    return (
        <div
            style={{
                display: 'flex',
                alignItems: 'flex-end',
                justifyContent: 'space-between',
                gap: 20,
                paddingBottom: 10,
                marginBottom: 18,
                borderBottom: '1px solid var(--line)',
            }}
        >
            <div style={{ display: 'flex', alignItems: 'baseline', gap: 12, minWidth: 0 }}>
                {index && (
                    <span className="kicker" style={{ color: 'var(--worm)', fontSize: 11 }}>
                        {index}
                    </span>
                )}
                <div style={{ minWidth: 0 }}>
                    <h2 style={{ margin: 0, fontSize: 20, letterSpacing: '0.01em' }}>{title}</h2>
                    {subtitle && (
                        <div style={{ fontSize: 13, color: 'var(--paper-dim)', marginTop: 3 }}>{subtitle}</div>
                    )}
                </div>
            </div>
            {meta && <div style={{ flexShrink: 0 }}>{meta}</div>}
        </div>
    );
}
