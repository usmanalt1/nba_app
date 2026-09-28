import { Panel } from '../ui/Panel';
import { StatCard } from '../ui/StatCard';
import { FormStrip } from '../ui/FormStrip';
import { CalibrationChart } from '../ui/CalibrationChart';
import { SectionHeader } from '../ui/SectionHeader';
import type { ModelStats } from '../../utils/modelStats';

interface HomeModelPulseProps {
    strategy: string | null;
    stats: ModelStats;
}

function formatSigned(value: number, digits = 1): string {
    return `${value >= 0 ? '+' : ''}${value.toFixed(digits)}`;
}

function Readout({ label, value, note }: { label: string; value: string; note?: string }) {
    return (
        <div style={{ minWidth: 0 }}>
            <div className="kicker" style={{ marginBottom: 6 }}>{label}</div>
            <div style={{ fontFamily: 'var(--mono)', fontSize: 18, color: 'var(--paper)' }}>{value}</div>
            {note && <div style={{ fontSize: 11, color: 'var(--paper-dim)', marginTop: 4 }}>{note}</div>}
        </div>
    );
}

export function HomeModelPulse({ strategy, stats }: HomeModelPulseProps) {
    if (stats.games === 0) return null;

    const { currentStreak } = stats;
    const streakLabel = currentStreak ? `${currentStreak.length}` : '—';
    const gapPoints = stats.calibrationGap * 100;
    // How much more often it backs the host than the host actually wins.
    const homeBias = (stats.homePickRate - stats.homeWinRate) * 100;

    return (
        <section style={{ marginBottom: 'var(--section-gap)' }}>
            <SectionHeader
                index="01"
                title="Model Tape"
                subtitle={`How ${strategy?.replace(/_/g, ' ') ?? 'the model'} has actually done, graded against results`}
                meta={<span className="kicker">{stats.games} games graded</span>}
            />

            <div
                style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))',
                    gap: 14,
                    marginBottom: 20,
                }}
            >
                <StatCard
                    hero
                    tone="brand"
                    label="Hit rate"
                    value={`${(stats.accuracy * 100).toFixed(1)}%`}
                    note={`${stats.hits} hit · ${stats.misses} miss`}
                />
                <StatCard
                    hero
                    label="Edge on a coin flip"
                    value={`${formatSigned(stats.edge)} pts`}
                    note="Accuracy above 50%"
                />
                <StatCard
                    hero
                    label="Calibration gap"
                    value={`${formatSigned(gapPoints)} pts`}
                    note={gapPoints > 0 ? 'Talks a bigger game than it plays' : 'Quietly better than it claims'}
                />
                <StatCard
                    hero
                    label={currentStreak?.hit ? 'Hit streak' : 'Cold streak'}
                    value={streakLabel}
                    tone={currentStreak?.hit ? 'win' : 'lose'}
                    note={`Best run this season: ${stats.bestStreak}`}
                />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)', gap: 20 }}>
                <Panel
                    accent
                    title="Form guide"
                    titleMeta={`last ${stats.form.length}`}
                    style={{ display: 'flex', flexDirection: 'column' }}
                >
                    <FormStrip form={stats.form} />

                    <div
                        style={{
                            display: 'grid',
                            gridTemplateColumns: 'repeat(3, minmax(0, 1fr))',
                            gap: 12,
                            marginTop: 22,
                        }}
                    >
                        {[10, 20, 40].map((window) => {
                            const rate = stats.rollingAccuracy(window);
                            return (
                                <Readout
                                    key={window}
                                    label={`Last ${window}`}
                                    value={rate === null ? '—' : `${(rate * 100).toFixed(0)}%`}
                                    note={rate === null ? 'not enough games' : 'hit rate'}
                                />
                            );
                        })}
                    </div>

                    <div
                        style={{
                            display: 'grid',
                            gridTemplateColumns: 'repeat(3, minmax(0, 1fr))',
                            gap: 12,
                            marginTop: 'auto',
                            paddingTop: 16,
                            borderTop: '1px solid var(--line)',
                        }}
                    >
                        <Readout label="Picked the home side" value={`${(stats.homePickRate * 100).toFixed(0)}%`} />
                        <Readout label="Home side actually won" value={`${(stats.homeWinRate * 100).toFixed(0)}%`} />
                        <Readout
                            label="Home-court bias"
                            value={`${formatSigned(homeBias, 0)} pts`}
                            note={homeBias > 0 ? 'Over-backs the host' : 'Under-backs the host'}
                        />
                    </div>
                </Panel>

                <Panel title="Calibration by confidence band">
                    <CalibrationChart buckets={stats.buckets} />
                </Panel>
            </div>
        </section>
    );
}
