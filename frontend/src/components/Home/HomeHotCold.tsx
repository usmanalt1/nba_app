import { useMemo, useState } from 'react';
import { SegmentedControl } from '@mantine/core';
import { Panel } from '../ui/Panel';
import { SectionHeader } from '../ui/SectionHeader';
import { DivergingRows, type DivergingRow } from '../ui/DivergingRows';
import { useHotAndCold } from '../../hooks/useHotAndCold';
import type { HotColdRow } from '../../types/hotCold';

type Scope = 'Players' | 'Teams';

interface HomeHotColdProps {
    index: string;
}

function signed(value: number | null | undefined, digits = 1): string {
    if (value === null || value === undefined) return '—';
    return `${value > 0 ? '+' : ''}${value.toFixed(digits)}`;
}

function playerRow(row: HotColdRow): DivergingRow {
    return {
        id: row.entity_id,
        label: row.name,
        teamKey: row.team_id,
        value: row.delta,
        note: `TS% ${signed(row.delta_ts_pct)}`,
        detail: `${row.name} — last 10: ${row.form.toFixed(1)} ppg · rest of season: ${row.baseline.toFixed(1)} · ${row.games} games`,
    };
}

function teamRow(row: HotColdRow): DivergingRow {
    const losses = (row.form_games ?? 0) - (row.form_wins ?? 0);
    return {
        id: row.entity_id,
        label: row.name,
        teamKey: row.team_id,
        value: row.delta,
        note: `${row.form_wins ?? 0}-${losses} L10`,
        detail: `${row.name} — last 10: ${signed(row.form)} margin · rest of season: ${signed(row.baseline)} · ${row.games} games`,
    };
}

export function HomeHotCold({ index }: HomeHotColdProps) {
    const [scope, setScope] = useState<Scope>('Players');
    const { data, loading, error } = useHotAndCold();

    const rows = useMemo<DivergingRow[]>(() => {
        const records = data?.records ?? [];
        return scope === 'Players'
            ? records.filter((row) => row.scope === 'player').map(playerRow)
            : records.filter((row) => row.scope === 'team').map(teamRow);
    }, [data, scope]);

    const forPlayers = scope === 'Players';
    const season = data?.season ?? null;

    return (
        <section style={{ marginBottom: 'var(--section-gap)' }}>
            <SectionHeader
                index={index}
                title="Hot & Cold"
                subtitle={
                    forPlayers
                        ? 'Who is scoring above or below their own season, over the last 10 games'
                        : 'Which teams are beating or trailing their own season, over the last 10 games'
                }
                meta={
                    <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                        {season && (
                            <span className="kicker" style={{ color: 'var(--paper-faint)' }}>
                                {season}{data?.season_is_fallback ? ' final' : ''}
                            </span>
                        )}
                        <SegmentedControl
                            size="xs"
                            value={scope}
                            onChange={(value) => setScope(value as Scope)}
                            data={['Players', 'Teams']}
                        />
                    </div>
                }
            />

            <Panel>
                {loading && <Empty>Working out who is running hot…</Empty>}

                {!loading && error && <Empty tone="lose">{error}</Empty>}

                {/* A null season means no season has reached the minimum yet - say so
                    rather than showing an empty panel. */}
                {!loading && !error && !season && (
                    <Empty>
                        The {data?.latest_season ?? 'new'} season is still too young — form needs{' '}
                        {data?.min_games ?? 20} games behind it. Back when there is a sample.
                    </Empty>
                )}

                {!loading && !error && season && rows.length === 0 && (
                    <Empty>Nobody has moved far enough off their season average to call.</Empty>
                )}

                {!loading && !error && season && rows.length > 0 && (
                    <DivergingRows
                        rows={rows}
                        legend={{ down: forPlayers ? 'Cold' : 'Sliding', up: forPlayers ? 'Hot' : 'Surging' }}
                        caption={
                            forPlayers
                                ? 'Bar length is points per game above or below the rest of their season.'
                                : 'Bar length is average margin above or below the rest of their season.'
                        }
                    />
                )}
            </Panel>
        </section>
    );
}

function Empty({ children, tone }: { children: React.ReactNode; tone?: 'lose' }) {
    return (
        <div style={{ fontSize: 13, color: tone === 'lose' ? 'var(--lose)' : 'var(--paper-faint)', padding: '8px 0' }}>
            {children}
        </div>
    );
}
