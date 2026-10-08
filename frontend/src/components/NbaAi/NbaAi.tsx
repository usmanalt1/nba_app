import { useState, type FormEvent, type ReactNode } from 'react';
import { Button, Textarea } from '@mantine/core';
import { Markdown } from '../ui/Markdown';
import { HeroStat, PageHero } from '../ui/PageHero';
import { Panel } from '../ui/Panel';
import { SectionHeader } from '../ui/SectionHeader';
import { apiFetch } from '../../lib/api';
import { useConversation } from '../../hooks/useConversation';
import type { ConversationExchange } from '../../types/conversation';

// Older entries carry asyncio's monotonic clock rather than a wall clock, which would
// render as 1970. Anything below this is from that format and gets no time.
const EPOCH_FLOOR_SECONDS = 1e9;

function askedAt(raw: string): string | null {
    const seconds = Number(raw);
    if (!Number.isFinite(seconds) || seconds < EPOCH_FLOOR_SECONDS) return null;

    const at = new Date(seconds * 1000);
    return `${at.toLocaleDateString(undefined, { month: 'short', day: 'numeric' })} · ${
        at.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })}`;
}

function Note({ children, tone }: { children: ReactNode; tone?: 'lose' }) {
    return (
        <div style={{ fontSize: 13, color: tone === 'lose' ? 'var(--lose)' : 'var(--paper-faint)', padding: '8px 0' }}>
            {children}
        </div>
    );
}

function Turn({ speaker, bright, children }: { speaker: string; bright?: boolean; children: ReactNode }) {
    return (
        <div>
            <span className="kicker" style={{ color: bright ? 'var(--paper)' : 'var(--paper-faint)' }}>{speaker}</span>
            <div style={{ marginTop: 6 }}>{children}</div>
        </div>
    );
}

function Exchange({ exchange, lead }: { exchange: ConversationExchange; lead: boolean }) {
    const time = askedAt(exchange.time_requested);

    return (
        <Panel accent={lead} style={{ marginBottom: 14 }}>
            <Turn speaker="You">
                {/* pre-wrap, not markdown: this is whatever the user typed. */}
                <p style={{ fontSize: 14, color: 'var(--paper)', whiteSpace: 'pre-wrap' }}>{exchange.question}</p>
            </Turn>
            <div style={{ marginTop: 14, paddingTop: 14, borderTop: '1px solid var(--line)' }}>
                <Turn speaker="Worm" bright>
                    <Markdown source={exchange.answer} />
                </Turn>
            </div>
            {time && (
                <div style={{ marginTop: 12, fontFamily: 'var(--mono)', fontSize: 11, color: 'var(--paper-faint)' }}>
                    {time}
                </div>
            )}
        </Panel>
    );
}

export function NbaAi() {
    const [question, setQuestion] = useState('');
    const [asking, setAsking] = useState(false);
    const [askError, setAskError] = useState<string | null>(null);
    const { exchanges, loading, error, reload } = useConversation();

    const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setAsking(true);
        setAskError(null);
        try {
            const response = await apiFetch('/api/nba/llm/ask', {
                method: 'POST',
                body: JSON.stringify({ question }),
            });
            const data = await response.json();
            if (!data.success) throw new Error(data.error ?? 'Worm could not answer that.');
            setQuestion('');
            reload();
        } catch (err) {
            setAskError(err instanceof Error ? err.message : 'Worm could not answer that.');
        } finally {
            setAsking(false);
        }
    };

    return (
        <div style={{ width: '100%', maxWidth: 1400, margin: '0 auto', paddingBottom: 60 }}>
            <PageHero
                eyebrow="Natural Language Stats"
                title="Ask Worm"
                blurb="Put a question in plain English. Worm answers off the warehouse it already has, not from memory, and shows the numbers it leaned on."
            >
                <HeroStat label="Questions this session" value={loading ? '—' : String(exchanges.length)} />
            </PageHero>

            <section style={{ marginBottom: 'var(--section-gap)' }}>
                <SectionHeader
                    index="01"
                    title="Your Question"
                    subtitle="Players, teams, seasons — anything the box scores can settle"
                />

                <Panel>
                    <form onSubmit={handleSubmit}>
                        <Textarea
                            placeholder="Who had the best season of LeBron's career?"
                            value={question}
                            onChange={(event) => setQuestion(event.currentTarget.value)}
                            minRows={3}
                            autosize
                            style={{ marginBottom: 14 }}
                        />
                        <Button type="submit" loading={asking} disabled={!question.trim()}>
                            Ask
                        </Button>
                    </form>

                    {askError && <Note tone="lose">{askError}</Note>}
                </Panel>
            </section>

            <section style={{ marginBottom: 'var(--section-gap)' }}>
                <SectionHeader
                    index="02"
                    title="Transcript"
                    subtitle="Everything asked this session, newest first"
                    meta={
                        exchanges.length > 0 && (
                            <span className="kicker">
                                {exchanges.length} {exchanges.length === 1 ? 'question' : 'questions'}
                            </span>
                        )
                    }
                />

                {loading && <Note>Reading the transcript…</Note>}
                {!loading && error && <Note tone="lose">{error}</Note>}
                {!loading && !error && exchanges.length === 0 && (
                    <Note>Nothing asked yet. The answers show up here.</Note>
                )}

                {exchanges.map((exchange, index) => (
                    <Exchange
                        key={`${exchange.time_requested}-${exchange.question}`}
                        exchange={exchange}
                        lead={index === 0}
                    />
                ))}
            </section>
        </div>
    );
}
