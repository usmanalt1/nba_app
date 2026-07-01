import { Select } from "@mantine/core";
import { useEffect, useState } from "react";
import NBADataTable from "../DataTable/NBADataTable";
import type { RawPlayerStats, PlayerStats} from '../../types/player';

export function Home() {

    const [players, setPlayers] = useState([]);
    const [teams, setTeams] = useState([]);
    const [seasons, setSeasons] = useState([]);
    const [selectedPlayer, setSelectedPlayer] = useState<string | null>(null);
    const [selectedTeam, setSelectedTeam] = useState<string | null>(null);
    const [selectedSeason, setSelectedSeason] = useState<string | null>(null);
    const [rows, setRows] = useState<PlayerStats[]>([]);

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
            .then(data => setRows(data.map((row: RawPlayerStats) => ({
                season: row.season_id,
                points: row.average_points,
                rebounds: row.average_rebounds,
                plusMinus: row.average_plus_minus,
                assists: row.average_assists,
            }))))
            .catch(() => {});
        return () => controller.abort();
    }, [selectedPlayer]);

    // Generate interface for these and change type
    const playerOptions = players.map((p: any) => ({
    value: String(p.player_id),
    label: p.player_name,
    }));


    const teamOptions = teams.map((p: any) => ({
    value: String(p.team_id),
    label: p.team_name,
    }));

    const seasonOptions = seasons.map((p: any) => ({
    value: String(p.season_name),
    label: String(p.season_name),
    }));
    


  return (
    <div>
        <div style={{ display: 'flex', gap: "16px", width: "100%", padding: "1px", marginBottom: '30px' }}>
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
        {rows.length > 0 && (
            <div style={{ marginTop: '30px' }}>
                <NBADataTable nbaData={rows} />
            </div>
        )}
    </div>
  );
}