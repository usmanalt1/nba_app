import type { CSSProperties } from 'react';
import wormSrc from '../../assets/worm.svg';

// A potrace silhouette: transparent where the portrait is lit, so it picks up the
// plate colour underneath and needs no cut-out background.
interface WormMarkProps {
    size?: number;
    /** Plate colour showing through the lit side of the portrait. */
    tone?: string;
    style?: CSSProperties;
}

export function WormMark({ size = 40, tone = 'var(--worm)', style }: WormMarkProps) {
    return (
        <span
            aria-hidden
            style={{
                width: size,
                height: size,
                borderRadius: '50%',
                background: tone,
                overflow: 'hidden',
                flexShrink: 0,
                display: 'block',
                ...style,
            }}
        >
            {/* Oversized and offset so the circle frames the face rather than the full plate. */}
            <img
                src={wormSrc}
                alt=""
                style={{
                    width: '210%',
                    height: '210%',
                    objectFit: 'cover',
                    objectPosition: '46% 8%',
                    display: 'block',
                    margin: '-14% 0 0 -52%',
                }}
            />
        </span>
    );
}

interface WormPortraitProps {
    height?: number;
    style?: CSSProperties;
}

export function WormPortrait({ height = 220, style }: WormPortraitProps) {
    const fade = 'linear-gradient(to right, transparent, #000 48%, #000 88%, transparent)';

    return (
        <div
            aria-hidden
            style={{
                height,
                width: height * 1.24,
                background: 'linear-gradient(115deg, var(--worm), var(--worm-deep))',
                overflow: 'hidden',
                flexShrink: 0,
                WebkitMaskImage: fade,
                maskImage: fade,
                ...style,
            }}
        >
            <img
                src={wormSrc}
                alt=""
                style={{ width: '100%', height: '100%', objectFit: 'cover', objectPosition: '50% 10%', display: 'block' }}
            />
        </div>
    );
}
