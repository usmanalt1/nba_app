import { Select } from "@mantine/core";
import { Table } from '@mantine/core';
import { useEffect, useState } from "react";

export function Home() {

    const [players, setPlayers] = useState([]);
    const [selected, setSelected] = useState(null);
    const [rows, setRows] = useState([])

    useEffect(() => {
    fetch("/api/nba/db/list_all_players")
        .then(r => r.json())
        .then(setPlayers);
    }, []);

    useEffect(() => {
        if (selected === null) return setRows([]);
        setRows([]);
        const controller = new AbortController();
        fetch(`/api/nba/db/get_player/${selected}`, { signal: controller.signal })
            .then(r => r.json())
            .then(setRows)
            .catch(() => {});
        return () => controller.abort();
    }, [selected]);

    const tableRow = selected !== null
        ? rows.map((row) => (
            <Table.Tr key={row.player_id}>
                <Table.Td>{row.season_id}</Table.Td>
                <Table.Td>{row.average_points}</Table.Td>
                <Table.Td>{row.average_rebounds}</Table.Td>
                <Table.Td>{row.average_plus_minus}</Table.Td>
                <Table.Td>{row.average_assists}</Table.Td>
            </Table.Tr>
        ))
        : null;

    const options = players.map((p) => ({
    value: String(p.player_id),
    label: p.player_name,
    }));


  return (
    <div style={{ padding: '20px' }}>
      <h1>Welcome to the NBA Data App</h1>
      <p>
        This application allows you to collect, view, and analyze NBA data. Use the navigation links to explore the features of the app.
      </p>
      <div >
        <Select
            label="Player"
            placeholder="Pick a player"
            data={options}
            value={selected}
            onChange={setSelected}
            searchable
        />
        <Table>
        <Table.Thead>
            <Table.Tr>
            <Table.Th>Season</Table.Th>
            <Table.Th>Points</Table.Th>
            <Table.Th>Rebounds</Table.Th>
            <Table.Th>Plus Minus</Table.Th>
            <Table.Th>Assists</Table.Th>
            </Table.Tr>
        </Table.Thead>
        <Table.Tbody>{tableRow}</Table.Tbody>
        </Table>
        </div>
    </div>
  );
}