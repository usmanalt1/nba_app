import React, { useEffect, useState } from 'react';
import { Textarea, Button, Text } from '@mantine/core';
import { Panel } from '../ui/Panel';
import { apiFetch } from '../../lib/api';

interface ConversationHistory {
    question: string;
    answer: string;
    time_requested: number;
}

export function NbaAi() {

    const [question, setQuestion] = useState('');
    const [answer, setAnswer] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [conversations, setConversations] = useState<ConversationHistory[]>([]);

    useEffect(() => {
        const fetchConversations = async () => {
            setLoading(true);
            setError(null);
            try {
                const response = await apiFetch('/api/nba/llm/get_conversation');
                const data = await response.json();
                setConversations(data.answers ?? []);

            } catch (err) {
                setError(err instanceof Error ? err.message : 'An unknown error occurred');
            } finally {
                setLoading(false);
            }
        };

        fetchConversations();
    }, [answer]); 

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setAnswer('');
        setLoading(true);
        setError(null);
        try {
            const response = await apiFetch('/api/nba/llm/ask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question }),
            });
            if (!response.ok) {
                throw new Error(`Error: ${response.statusText}`);
            }
            const data = await response.json();
            setAnswer(data.answer);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'An unknown error occurred');
        } finally {
            setLoading(false);
        }
    }

    return (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%', height: '95vh' }}>
            <h1 style={{ width: '100%' }}>NBA AI</h1>
            <p style={{ width: '100%', marginBottom: '20px' }}>Gain insights about the NBA, and it will answer using data from our database.</p>

            <div style={{ width: '100%', flex: 1, minHeight: 0, overflowY: 'auto', marginTop: '10px'}}>
                {conversations.length > 0 && (
                    <div style={{ width: '100%' }}>
                        {conversations.map((conv, index) => (
                            <Panel key={index} style={{ marginBottom: '14px' }}>
                                <strong>Q: {conv.question}</strong><br />
                                <strong>A:</strong> {conv.answer}
                            </Panel>
                        ))}
                    </div>
                )}

                {error && <Text color="red" style={{ marginBottom: '10px' }}>{error}</Text>}
            </div>

            <div style={{ width: '100%', display: 'flex', justifyContent: 'left', marginTop: '20px' }}>
                <form onSubmit={handleSubmit} style={{ width: '100%' }}>
                    <Textarea
                        placeholder="Ask the AI a question about the NBA..."
                        value={question}
                        onChange={(e) => setQuestion(e.currentTarget.value)}
                        minRows={3}
                        style={{ width: '100%', marginBottom: '10px' }}
                    />
                    <Button type="submit" loading={loading} disabled={!question.trim()} style={{ marginBottom: '10px' }}>
                        Ask
                    </Button>
                </form>
            </div>
        </div>
    );
}