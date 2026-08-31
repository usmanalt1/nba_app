import type { CSSProperties, ReactNode } from 'react';

interface PanelProps {
    title?: string;
    children: ReactNode;
    style?: CSSProperties;
}

// Plain div rather than Mantine's Box: Box's w/h/p shorthands are rem-based and this
// app sets a non-default 18px root font-size for typography, which silently scales
// those props by 1.125x and throws off layout math done in raw pixels elsewhere.
export function Panel({ title, children, style }: PanelProps) {
    return (
        <div
            style={{
                border: '1px solid var(--line)',
                borderRadius: 4,
                padding: '18px 20px',
                background: 'var(--panel)',
                color: 'var(--paper)',
                boxSizing: 'border-box',
                ...style,
            }}
        >
            {title && (
                <div
                    style={{
                        fontFamily: "'IBM Plex Mono', monospace",
                        fontSize: '10px',
                        letterSpacing: '0.06em',
                        textTransform: 'uppercase',
                        color: 'var(--paper-dim)',
                        marginBottom: 14,
                    }}
                >
                    {title}
                </div>
            )}
            {children}
        </div>
    );
}
