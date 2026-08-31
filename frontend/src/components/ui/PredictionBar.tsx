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
    const hasResult = actualHomeWin !== undefined;
    const correct = hasResult && predictedHomeWin === actualHomeWin;

    // the name row's width split roughly tracks the bar's split so the two visually
    // correspond, clamped so neither side collapses to unreadable width on lopsided games
    const awayFlex = Math.min(Math.max(awayPct, 30), 70);
    const homeFlex = 100 - awayFlex;

    return (
        <Panel style={{ width: 280, flexShrink: 0 }}>
            <div
                style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: 10,
                    fontFamily: "'IBM Plex Mono', monospace",
                }}
            >
                <span style={{ fontSize: 10, letterSpacing: '0.06em', textTransform: 'uppercase', color: 'var(--paper-dim)' }}>
                    {gameDate ? new Date(gameDate).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }) : ''}
                </span>
                {hasResult && (
                    <span style={{ fontSize: 11, fontWeight: 700, color: correct ? 'var(--win)' : 'var(--lose)' }}>
                        {correct ? 'CORRECT' : 'INCORRECT'}
                    </span>
                )}
            </div>

            <div style={{ display: 'flex', gap: 8, fontSize: 13, marginBottom: 6 }}>
                <div style={{ flex: `0 0 ${awayFlex}%`, minWidth: 0 }}>
                    <span
                        title={awayTeam}
                        style={{
                            display: 'block',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                            color: 'var(--away)',
                            fontWeight: predictedHomeWin === false ? 700 : 400,
                        }}
                    >
                        {awayTeam}{typeof awayPts === 'number' ? ` — ${awayPts}` : ''}
                    </span>
                    <span style={{ fontSize: 11, color: 'var(--paper-dim)' }}>{awayPct}%</span>
                </div>
                <div style={{ flex: `0 0 ${homeFlex}%`, minWidth: 0, textAlign: 'right' }}>
                    <span
                        title={homeTeam}
                        style={{
                            display: 'block',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                            color: 'var(--home)',
                            fontWeight: predictedHomeWin ? 700 : 400,
                        }}
                    >
                        {homeTeam}{typeof homePts === 'number' ? ` — ${homePts}` : ''}
                    </span>
                    <span style={{ fontSize: 11, color: 'var(--paper-dim)' }}>{homePct}%</span>
                </div>
            </div>

            <div
                style={{
                    height: 8,
                    borderRadius: 4,
                    background: `linear-gradient(to right, var(--away) ${awayPct}%, var(--home) ${awayPct}%)`,
                }}
            />
        </Panel>
    );
}
