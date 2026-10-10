import { WormMark } from '../ui/WormMark';

export function Logo({ compact = false }: { compact?: boolean }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: compact ? 10 : 12 }}>
      <WormMark size={compact ? 32 : 44} />
      <div style={{ lineHeight: 1 }}>
        <div
          style={{
            fontFamily: 'var(--heading)',
            fontSize: compact ? 22 : 30,
            fontWeight: 700,
            letterSpacing: '0.06em',
            color: 'var(--paper)',
            textTransform: 'uppercase',
          }}
        >
          Worm
        </div>
        {!compact && (
          <div className="kicker" style={{ marginTop: 4, fontSize: 9 }}>
            NBA Prediction Lab
          </div>
        )}
      </div>
    </div>
  );
}
