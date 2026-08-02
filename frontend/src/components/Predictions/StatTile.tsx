import { Text} from "@mantine/core";

export function StatTile({ label, value }: { label: string; value: string }) {
    return (
        <div style={{ border: '1px solid var(--line)', background: 'var(--panel)', borderRadius: 4, padding: '16px 18px' }}>
            <Text size="10px" c="var(--paper-dim)" tt="uppercase" ff="'IBM Plex Mono', monospace" style={{ letterSpacing: '0.06em', marginBottom: 8 }}>{label}</Text>
            <Text size="26px" fw={600} ff="'Oswald', sans-serif" c="var(--paper)">{value}</Text>
        </div>
    );
}