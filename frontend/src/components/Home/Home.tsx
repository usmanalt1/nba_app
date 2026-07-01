import { Select } from "@mantine/core";
import { Table } from '@mantine/core';
import { useEffect, useState } from "react";

export function Home() {

    const [players, setPlayers] = useState([]);
    const [teams, setTeams] = useState([]);
    const [seasons, setSeasons] = useState([]);
    const [selectedPlayer, setSelectedPlayer] = useState(null);
    const [selectedTeam, setSelectedTeam] = useState(null);
    const [selectedSeason, setSelectedSeason] = useState(null);
    const [rows, setRows] = useState([])

    useEffect(() => {
    if (selectedSeason === null || selectedTeam === null) return setSelectedPlayer(null);
    setSelectedPlayer(null);
    fetch(`/api/nba/db/list_all_players/${selectedSeason}/${selectedTeam}`)
        .then(r => r.json())
        .then(setPlayers);
    }, [selectedSeason, selectedTeam]);

    useEffect(() => {
    fetch("/api/nba/db/list_all_seasons")
        .then(r => r.json())
        .then(setSeasons);
    }, []);

    useEffect(() => {
    fetch("/api/nba/db/list_all_teams")
        .then(r => r.json())
        .then(setTeams);
    }, []);

    useEffect(() => {
        if (selectedPlayer === null) return setRows([]);
        setRows([]);
        const controller = new AbortController();
        fetch(`/api/nba/db/get_player/${selectedPlayer}`, { signal: controller.signal })
            .then(r => r.json())
            .then(setRows)
            .catch(() => {});
        return () => controller.abort();
    }, [selectedPlayer]);

    const tableRow = selectedPlayer !== null
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

    const playerOptions = players.map((p) => ({
    value: String(p.player_id),
    label: p.player_name,
    }));


    const teamOptions = teams.map((p) => ({
    value: String(p.team_id),
    label: p.team_name,
    }));

    const seasonOptions = seasons.map((p) => ({
    value: String(p.season_name),
    label: String(p.season_name),
    }));
    


  return (
    <div style={{ padding: '20px' }}>
      <h1>Welcome to the NBA Data App</h1>
      <p>
        This application allows you to collect, view, and analyze NBA data. Use the navigation links to explore the features of the app.
      </p>
    <div style={{ display: 'flex', gap: "16px", width: "100%", padding: "1px" }}>
    <Select
        style={{ flex: 1 }}
        label="Season"
        placeholder="Pick a Season"
        data={seasonOptions}
        value={selectedSeason}
        onChange={setSelectedSeason}
        searchable
    />
    <Select
        style={{ flex: 1 }}
        label="Team"
        placeholder="Pick a Team"
        data={teamOptions}
        value={selectedTeam}
        onChange={setSelectedTeam}
        searchable
    />
    <Select
        style={{ flex: 1 }}
        label="Player"
        placeholder="Pick a player"
        data={playerOptions}
        value={selectedPlayer}
        onChange={setSelectedPlayer}
        searchable
    />
    </div>
    <div>
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