import { Panel } from './Panel';

interface PredictionBarProps {
    homeTeam: string;
    awayTeam: string;
    homeWinProbability: number;
    homePts?: number;
    awayPts?: number;
    predictedHomeWin?: boolean;
    actualHomeWin?: boolean;
    gameDate?: string;
}

interface SideProps {
    team: string;
    pct: number;
    pts?: number;
    color: string;
    picked: boolean;
}

function Side({ team, pct, pts, color, picked }: SideProps) {
    return (
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '3px 0' }}>
            <span style={{ width: 7, height: 7, borderRadius: '50%', background: color, flexShrink: 0 }} />
            <span
                title={team}
                style={{
                    flex: 1,
                    minWidth: 0,
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                    fontSize: 13,
                    fontWeight: picked ? 600 : 400,
                    color: picked ? 'var(--paper)' : 'var(--paper-dim)',
                }}
            >
                {team}
            </span>
            {typeof pts === 'number' && (
                <span style={{ fontFamily: 'var(--mono)', fontSize: 13, color: 'var(--paper)', fontVariantNumeric: 'tabular-nums' }}>
                    {pts}
                </span>
            )}
            <span
                style={{
                    fontFamily: 'var(--mono)',
                    fontSize: 12,
                    color: picked ? 'var(--paper)' : 'var(--paper-dim)',
                    fontVariantNumeric: 'tabular-nums',
                    width: 34,
                    textAlign: 'right',
                }}
            >
                {pct}%
            </span>
        </div>
    );
}

export function PredictionBar({
    homeTeam,
    awayTeam,
    homeWinProbability,
    homePts,
    awayPts,
    predictedHomeWin,
    actualHomeWin,
    gameDate,
}: PredictionBarProps) {
    const homePct = Math.round(homeWinProbability * 100);
    const awayPct = 100 - homePct;
    const hasResult = typeof actualHomeWin === 'boolean';
    const correct = hasResult && predictedHomeWin === actualHomeWin;

    return (
        <Panel style={{ width: 284, flexShrink: 0 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
                <span className="kicker">
                    {gameDate ? new Date(gameDate).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : ''}
                </span>
                {hasResult && (
                    <span
                        className="kicker"
                        style={{ color: correct ? 'var(--win)' : 'var(--lose)', fontWeight: 600 }}
                    >
                        {correct ? '✓ Hit' : '✕ Miss'}
                    </span>
                )}
            </div>

            {/* Stacked rather than side-by-side: full-length NBA team names need the
                whole card width or they all truncate to "Golden State ...". */}
            <Side team={awayTeam} pct={awayPct} pts={awayPts} color="var(--away)" picked={predictedHomeWin === false} />
            <Side team={homeTeam} pct={homePct} pts={homePts} color="var(--home)" picked={predictedHomeWin === true} />

            {/* 2px surface gap between the two fills rather than a stroke around them. */}
            <div style={{ display: 'flex', gap: 2, height: 6, marginTop: 10 }}>
                <div style={{ width: `${awayPct}%`, background: 'var(--away)', borderRadius: '3px 0 0 3px' }} />
                <div style={{ flex: 1, background: 'var(--home)', borderRadius: '0 3px 3px 0' }} />
            </div>
        </Panel>
    );
}
