import type { CSSProperties } from 'react';
import wormSrc from '../../assets/worm.svg';

/**
 * The logo is a potrace silhouette: opaque black where the portrait is shaded,
 * transparent where it is lit. Laid over a coloured plate the lit areas pick up
 * the plate colour while the black shading sinks into the page, which is why the
 * mark never needs a cut-out background.
 */
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
    /** Width of the portrait plate; height follows the source aspect ratio. */
    height?: number;
    style?: CSSProperties;
}

/** Full-bleed hero treatment: the same portrait, faded into the page from the left. */
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
