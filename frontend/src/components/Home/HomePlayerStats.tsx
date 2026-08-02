import type { RawPlayerStats, PlayerStats } from '../../types/player';
import { useEffect, useState } from "react";
import { Select } from "@mantine/core";
import NBADataTable from "../DataTable/NBADataTable";

interface HomePlayerStatsProps {
    selectedPlayer: string | null;
    selectedTeam: string | null;
    selectedSeason: string | null;
    rows: PlayerStats[];
    setSelectedPlayer: (value: string | null) => void;
    setSelectedTeam: (value: string | null) => void;
    setSelectedSeason: (value: string | null) => void;
    setRows: (value: PlayerStats[]) => void;
}
export default function HomePlayerStats(props: HomePlayerStatsProps) {
    const [players, setPlayers] = useState([]);
    const [teams, setTeams] = useState([]);
    const [seasons, setSeasons] = useState([]);
    

useEffect(() => {
    if (props.selectedSeason === null || props.selectedTeam === null) {
        props.setSelectedPlayer(null);
        return;
    }
    fetch(`/api/nba/db/list_all_players/${props.selectedSeason}/${props.selectedTeam}`)
        .then(r => r.json())
        .then(setPlayers);
}, [props.selectedSeason, props.selectedTeam]);

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
        if (props.selectedPlayer === null) return props.setRows([]);
        const controller = new AbortController();
        fetch(`/api/nba/db/get_player/${props.selectedPlayer}`, { signal: controller.signal })
            .then(r => r.json())
            .then(data => props.setRows(data.map((row: RawPlayerStats) => ({
                season: row.season_id,
                points: row.average_points,
                rebounds: row.average_rebounds,
                plusMinus: row.average_plus_minus,
                assists: row.average_assists,
            }))))
            .catch(() => { });
        return () => controller.abort();
    }, [props.selectedPlayer]);

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

    return <>
        <div style={{ display: 'flex', gap: "16px", width: "100%", padding: "1px", marginBottom: '30px' }}>
            <Select
                style={{ flex: 1 }}
                label="Season"
                placeholder="Pick a Season"
                data={seasonOptions}
                value={props.selectedSeason}
                onChange={props.setSelectedSeason}
                searchable
            />
            <Select
                style={{ flex: 1 }}
                label="Team"
                placeholder="Pick a Team"
                data={teamOptions}
                value={props.selectedTeam}
                onChange={props.setSelectedTeam}
                searchable
            />
            <Select
                style={{ flex: 1 }}
                label="Player"
                placeholder="Pick a player"
                data={playerOptions}
                value={props.selectedPlayer}
                onChange={props.setSelectedPlayer}
                searchable
            />
        </div>
        {
            props.rows.length > 0 && (
                <div style={{ marginTop: '10px', width: '100%', border: '1px solid var(--line)', borderRadius: 4, padding: '1px', fontFamily: "'IBM Plex Mono', monospace" }}>
                    <NBADataTable nbaData={props.rows} />
                </div>
            )
        }
    </>

}