import { WormMark } from '../ui/WormMark';

export function Logo() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
      <WormMark size={44} />
      <div style={{ lineHeight: 1 }}>
        <div
          style={{
            fontFamily: 'var(--heading)',
            fontSize: 30,
            fontWeight: 700,
            letterSpacing: '0.06em',
            color: 'var(--paper)',
            textTransform: 'uppercase',
          }}
        >
          Worm
        </div>
        <div className="kicker" style={{ marginTop: 4, fontSize: 9 }}>
          NBA Prediction Lab
        </div>
      </div>
    </div>
  );
}
