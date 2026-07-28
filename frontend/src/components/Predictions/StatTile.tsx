import { Text} from "@mantine/core";

export function StatTile({ label, value }: { label: string; value: string }) {
    return (
        <div style={{ border: '1px solid var(--mantine-color-blue-4)', borderRadius: 'var(--mantine-radius-md)', padding: '12px' }}>
            <Text size="sm" c="dimmed">{label}</Text>
            <Text size="xl" fw={700}>{value}</Text>
        </div>
    );
}