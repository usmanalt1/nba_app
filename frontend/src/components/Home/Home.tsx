import { Select } from "@mantine/core";

import { useEffect, useState } from "react";

export function Home() {

    const [players, setPlayers] = useState([]);
    const [selected, setSelected] = useState(null);

    useEffect(() => {
    fetch("/api/nba/db/list_all_players")
        .then(r => r.json())
        .then(setPlayers);
    }, []);

    const options = players.map((p) => ({
    value: String(p.id),
    label: p.full_name,
    }));
    console.log(players)
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
        </div>
    </div>
  );
}