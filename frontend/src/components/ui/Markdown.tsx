import type { CSSProperties, ReactNode } from 'react';

type Block =
    | { kind: 'heading'; level: number; text: string }
    | { kind: 'paragraph'; text: string }
    | { kind: 'list'; ordered: boolean; items: string[] }
    | { kind: 'table'; head: string[]; rows: string[][] };

const HEADING = /^(#{1,6})\s+(.*)$/;
const BULLET = /^\s*[-*+]\s+/;
const ORDERED = /^\s*\d+[.)]\s+/;
const INLINE = /\*\*([^*]+)\*\*|\*([^*]+)\*|`([^`]+)`/g;

function isTableRow(line: string): boolean {
    return line.trim().startsWith('|');
}

/** The |---|:--:| line under a table's header row. */
function isTableDivider(line: string): boolean {
    const bare = line.replace(/[|\s]/g, '');
    return bare.length > 0 && /^[:-]+$/.test(bare);
}

function splitRow(line: string): string[] {
    return line.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map(cell => cell.trim());
}

function startsBlock(line: string): boolean {
    return HEADING.test(line) || BULLET.test(line) || ORDERED.test(line) || isTableRow(line);
}

function parseBlocks(source: string): Block[] {
    const lines = source.replace(/\r\n/g, '\n').split('\n');
    const blocks: Block[] = [];
    let i = 0;

    while (i < lines.length) {
        const line = lines[i];
        if (!line.trim()) { i += 1; continue; }

        const heading = HEADING.exec(line);
        if (heading) {
            blocks.push({ kind: 'heading', level: heading[1].length, text: heading[2] });
            i += 1;
            continue;
        }

        // Needs the divider on the next line, or a stray "|" line would start a table.
        if (isTableRow(line) && isTableDivider(lines[i + 1] ?? '')) {
            const head = splitRow(line);
            i += 2;
            const rows: string[][] = [];
            while (i < lines.length && isTableRow(lines[i])) {
                rows.push(splitRow(lines[i]));
                i += 1;
            }
            blocks.push({ kind: 'table', head, rows });
            continue;
        }

        const marker = BULLET.test(line) ? BULLET : ORDERED.test(line) ? ORDERED : null;
        if (marker) {
            const items: string[] = [];
            while (i < lines.length && marker.test(lines[i])) {
                items.push(lines[i].replace(marker, ''));
                i += 1;
            }
            blocks.push({ kind: 'list', ordered: marker === ORDERED, items });
            continue;
        }

        const paragraph: string[] = [];
        while (i < lines.length && lines[i].trim() && !startsBlock(lines[i])) {
            paragraph.push(lines[i].trim());
            i += 1;
        }
        blocks.push({ kind: 'paragraph', text: paragraph.join(' ') });
    }

    return blocks;
}

function inline(text: string): ReactNode[] {
    const nodes: ReactNode[] = [];
    const pattern = new RegExp(INLINE.source, 'g');
    let last = 0;
    let match: RegExpExecArray | null;

    while ((match = pattern.exec(text)) !== null) {
        if (match.index > last) nodes.push(text.slice(last, match.index));
        const [raw, bold, italic, code] = match;
        const key = `${match.index}-${raw.length}`;

        if (bold) nodes.push(<strong key={key} style={{ fontWeight: 600 }}>{bold}</strong>);
        else if (italic) nodes.push(<em key={key} style={{ color: 'var(--paper-dim)' }}>{italic}</em>);
        else nodes.push(<code key={key}>{code}</code>);

        last = match.index + raw.length;
    }

    if (last < text.length) nodes.push(text.slice(last));
    return nodes;
}

function Table({ head, rows }: { head: string[]; rows: string[][] }) {
    // First column is the label, the rest figures; the divider's alignment is ignored.
    const cell = (index: number): CSSProperties => ({
        padding: '9px 12px',
        textAlign: index === 0 ? 'left' : 'right',
        fontFamily: index === 0 ? 'inherit' : 'var(--mono)',
        fontVariantNumeric: index === 0 ? 'normal' : 'tabular-nums',
    });

    return (
        <div style={{ overflowX: 'auto', border: '1px solid var(--line)', borderRadius: 4, margin: '12px 0' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                <thead>
                    <tr>
                        {head.map((heading, column) => (
                            <th
                                key={column}
                                className="kicker"
                                style={{
                                    ...cell(column),
                                    fontFamily: 'var(--mono)',
                                    background: 'var(--panel-2)',
                                    borderBottom: '1px solid var(--line)',
                                    whiteSpace: 'nowrap',
                                }}
                            >
                                {heading}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {rows.map((row, index) => (
                        <tr key={index}>
                            {row.map((value, column) => (
                                <td
                                    key={column}
                                    style={{
                                        ...cell(column),
                                        color: 'var(--paper)',
                                        borderBottom: index === rows.length - 1 ? 'none' : '1px solid var(--line)',
                                    }}
                                >
                                    {inline(value)}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}

/** Only what the LLM emits; anything else falls through as plain text. */
export function Markdown({ source }: { source: string }) {
    const blocks = parseBlocks(source ?? '');

    return (
        <div style={{ fontSize: 14, color: 'var(--paper)', lineHeight: 1.5 }}>
            {blocks.map((block, index) => {
                if (block.kind === 'heading') {
                    return (
                        <div
                            key={index}
                            style={{
                                fontFamily: 'var(--heading)',
                                fontWeight: 600,
                                fontSize: block.level <= 2 ? 15 : 13,
                                textTransform: 'uppercase',
                                letterSpacing: '0.01em',
                                margin: index === 0 ? '0 0 10px' : '18px 0 10px',
                            }}
                        >
                            {inline(block.text)}
                        </div>
                    );
                }

                if (block.kind === 'table') {
                    return <Table key={index} head={block.head} rows={block.rows} />;
                }

                if (block.kind === 'list') {
                    const List = block.ordered ? 'ol' : 'ul';
                    return (
                        <List key={index} style={{ margin: '10px 0', paddingLeft: 20 }}>
                            {block.items.map((item, position) => (
                                <li key={position} style={{ marginBottom: 6 }}>{inline(item)}</li>
                            ))}
                        </List>
                    );
                }

                return (
                    <p key={index} style={{ margin: index === 0 ? '0 0 10px' : '10px 0' }}>
                        {inline(block.text)}
                    </p>
                );
            })}
        </div>
    );
}
