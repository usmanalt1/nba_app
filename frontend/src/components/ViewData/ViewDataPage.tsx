import { apiFetch } from "../../lib/api";
import NBADataTable from "../DataTable/NBADataTable";
import TeamDataTable from "../DataTable/TeamDataTable";
import { AdvancedPlayerTable, AdvancedTeamTable } from "../DataTable/AdvancedDataTable";
import { Select, TextInput } from "@mantine/core";
import { useState, useEffect, type CSSProperties } from "react";
import type { SeasonOption, SeasonPlayerStats } from "../../types/player";
import type { SeasonTeamStats } from "../../types/team";
import type { SeasonAdvancedPlayerStats, SeasonAdvancedTeamStats } from "../../types/stats";
import { useViewDataFilters } from "./ViewDataFiltersContext";

// Mirrors the Mantine "pills" tabs below: worm accent when active, dim paper when not.
const stageButtonStyle: CSSProperties = {
    flex: 1,
    padding: '6px 14px',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer',
    backgroundColor: 'transparent',
    color: 'var(--paper-dim)',
    fontFamily: "'IBM Plex Mono', monospace",
    fontSize: '14px',
    fontWeight: 700,
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
};

const stageButtonActiveStyle: CSSProperties = {
    backgroundColor: 'var(--worm)',
    color: 'var(--paper)',
};

// Each filter group is its own pill container; the row's gap separates them.
const toggleGroupStyle: CSSProperties = {
    display: 'flex',
    gap: '4px',
    alignItems: 'center',
    padding: '4px',
    border: '1px solid var(--line)',
    borderRadius: '4px',
    backgroundColor: 'var(--panel)',
};

const selectStyle: CSSProperties = {
    flex: 1,
};

export function ViewDataPage() {
    const [seasons, setSeasons] = useState<SeasonOption[]>([]);
    const [teams, setTeams] = useState([]);
    const {
        viewMode, setViewMode,
        statSet, setStatSet,
        selectedSeason, setSelectedSeason,
        selectedTeam, setSelectedTeam,
        selectedStage, setSelectedStage,
        selectedPosition, setSelectedPosition,
        playerQuery, setPlayerQuery,
    } = useViewDataFilters();
    const [rows, setRows] = useState<SeasonPlayerStats[]>([]);
    const [teamRows, setTeamRows] = useState<SeasonTeamStats[]>([]);
    const [advPlayerRows, setAdvPlayerRows] = useState<SeasonAdvancedPlayerStats[]>([]);
    const [advTeamRows, setAdvTeamRows] = useState<SeasonAdvancedTeamStats[]>([]);
    const [loading, setLoading] = useState(false);

    // Default to the newest season so the table has data on first paint.
    useEffect(() => {
        apiFetch("/api/nba/db/list_all_seasons?has_stats=true")
            .then(r => r.json())
            .then((data: SeasonOption[]) => {
                setSeasons(data);
                const latest = [...data]
                    .sort((a, b) => String(a.season_name).localeCompare(String(b.season_name)))
                    .at(-1);
                // Only a default: the updater form reads the live value, so coming
                // back to this page keeps whatever season the user had picked.
                if (latest) setSelectedSeason(current => current ?? String(latest.season_name));
            });
    }, []);

    useEffect(() => {
        apiFetch("/api/nba/db/list_all_teams")
            .then(r => r.json())
            .then(setTeams);
    }, []);

    useEffect(() => {
        if (selectedSeason === null) {
            setRows([]);
            setTeamRows([]);
            setAdvPlayerRows([]);
            setAdvTeamRows([]);
            return;
        }
        const params = new URLSearchParams({
            season_name: selectedSeason,
            season_type: selectedStage === "Playoffs" ? "playoffs" : "regular",
        });
        if (selectedTeam !== null) params.set("team_id", selectedTeam);

        // Four endpoints share these filters; only the active view is fetched.
        const teams = viewMode === "Teams";
        const advanced = statSet === "Advanced";
        const endpoint = advanced
            ? (teams ? "season_advanced_team_stats" : "season_advanced_player_stats")
            : (teams ? "season_team_stats" : "season_player_stats");

        const controller = new AbortController();
        setLoading(true);
        apiFetch(`/api/nba/db/${endpoint}?${params}`, { signal: controller.signal })
            .then(r => r.json())
            .then(data => {
                if (advanced) return teams ? setAdvTeamRows(data) : setAdvPlayerRows(data);
                return teams ? setTeamRows(data) : setRows(data);
            })
            .then(() => setLoading(false))
            .catch(() => { });
        return () => controller.abort();
    }, [selectedSeason, selectedTeam, selectedStage, viewMode, statSet]);

    const seasonOptions = seasons.map((p: any) => ({
        value: String(p.season_name),
        label: String(p.season_name),
    }));

    const teamOptions = teams.map((t: any) => ({
        value: String(t.team_id),
        label: t.team_name,
    }));

    // The roster feed gives coarse positions - G, F, C and hyphenated combos
    // like G-F - so these are the only values that can actually match.
    const positionOptions = ["G", "F", "C"];

    // Derived, not state: with no position picked and an empty box, every row
    // passes through, which is why the full season shows by default.
    const query = playerQuery.trim().toLowerCase();
    const visibleRows = rows.filter(row => {
        // Split on the hyphen so a "G-F" player is listed under both G and F.
        const positions = (row.position ?? "").toUpperCase().split("-");
        const matchesPosition = selectedPosition === null || positions.includes(selectedPosition);
        const matchesQuery = query === ""
            || row.player_name.toLowerCase().includes(query);
        return matchesPosition && matchesQuery;
    });

    const visibleTeamRows = query === ""
        ? teamRows
        : teamRows.filter(row => row.team_name.toLowerCase().includes(query));

    // One name filter for every shape: players carry player_name, teams team_name.
    const byName = <T extends { player_name?: string | null; team_name?: string | null }>(list: T[]) =>
        query === ""
            ? list
            : list.filter(r => (r.player_name ?? r.team_name ?? "").toLowerCase().includes(query));

    const visibleAdvPlayers = byName(advPlayerRows);
    const visibleAdvTeams = byName(advTeamRows);

    const showingTeams = viewMode === "Teams";
    const showingAdvanced = statSet === "Advanced";

    const visibleCount = showingAdvanced
        ? (showingTeams ? visibleAdvTeams.length : visibleAdvPlayers.length)
        : (showingTeams ? visibleTeamRows.length : visibleRows.length);
    const totalCount = showingAdvanced
        ? (showingTeams ? advTeamRows.length : advPlayerRows.length)
        : (showingTeams ? teamRows.length : rows.length);

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4, height: '100%', minHeight: 0 }}>
            <div
                style={{
                    fontFamily: 'var(--heading)',
                    fontSize: 90,
                    fontWeight: 700,
                    color: 'var(--paper)',
                    textTransform: 'uppercase',
                }}
            >
                Can of Worms
                <div className="kicker" style={{ fontSize: 12, margin: 0 }}>
                    <p>Detailed statisics allowing you insights into everything NBA</p>
                </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '20px' }}>
                <div style={toggleGroupStyle}>
                    {(["Basic", "Advanced"] as const).map(set => (
                        <button
                            key={set}
                            style={{ ...stageButtonStyle, ...(statSet === set ? stageButtonActiveStyle : null) }}
                            onClick={() => setStatSet(set)}
                        >
                            {set}
                        </button>
                    ))}
                </div>
                <div style={toggleGroupStyle}>
                    {(["Players", "Teams"] as const).map(mode => (
                        <button
                            key={mode}
                            style={{ ...stageButtonStyle, ...(viewMode === mode ? stageButtonActiveStyle : null) }}
                            onClick={() => setViewMode(mode)}
                        >
                            {mode}
                        </button>
                    ))}
                </div>
                <Select style={selectStyle}
                    placeholder="Pick a Season"
                    data={seasonOptions}
                    value={selectedSeason}
                    onChange={setSelectedSeason}
                    searchable
                />
                <div style={toggleGroupStyle}>
                    {(["Regular", "Playoffs"] as const).map(stage => (
                        <button
                            key={stage}
                            style={{ ...stageButtonStyle, ...(selectedStage === stage ? stageButtonActiveStyle : null) }}
                            onClick={() => setSelectedStage(stage)}
                        >
                            {stage}
                        </button>
                    ))}
                </div>
                <Select style={selectStyle}
                    placeholder="All Teams"
                    data={teamOptions}
                    value={selectedTeam}
                    onChange={setSelectedTeam}
                    clearable
                    searchable
                />
            </div>
            <div style={{ display: 'flex', alignItems: 'center', marginTop: '10px', width: '30%', gap: '10px' }}>
                <TextInput
                    style={selectStyle}
                    placeholder={showingTeams ? "Search for a team" : "Search for a player"}
                    value={playerQuery}
                    onChange={event => setPlayerQuery(event.currentTarget.value)}
                />
                {/* Teams have no position, so the pills only show for players. */}
                {!showingTeams && (
                    <div style={toggleGroupStyle}>
                        {positionOptions.map(position => (
                            <button
                                key={position}
                                style={{ ...stageButtonStyle, ...(selectedPosition === position ? stageButtonActiveStyle : null) }}
                                // Clicking the active position clears it, since there is no "All" pill.
                                onClick={() => setSelectedPosition(current => current === position ? null : position)}
                            >
                                {position}
                            </button>
                        ))}
                    </div>
                )}
            </div>

            <div style={{ marginTop: '24px', flex: 1, minHeight: 0, display: 'flex', flexDirection: 'column' }}>
                <p style={{ color: 'var(--paper-faint)', fontSize: 12, margin: '0 0 10px', flexShrink: 0 }}>
                    {loading
                        ? 'Loading\u2026'
                        : `${visibleCount}${visibleCount === totalCount ? '' : ` of ${totalCount}`} ${showingTeams ? 'teams' : 'players'}`}
                </p>
                {/* Definite height from flex, so the table's height:100% resolves. */}
                <div style={{ flex: 1, minHeight: 0 }}>
                    {showingAdvanced
                        ? (showingTeams
                            ? <AdvancedTeamTable rows={visibleAdvTeams} />
                            : <AdvancedPlayerTable rows={visibleAdvPlayers} />)
                        : (showingTeams
                            ? <TeamDataTable teamData={visibleTeamRows} />
                            : <NBADataTable nbaData={visibleRows} />)}
                </div>
                {!loading && visibleCount === 0 && (
                    <p style={{ color: 'var(--paper-faint)', fontSize: 14, marginTop: '10px' }}>
                        No {showingTeams ? 'teams' : 'players'} match these filters.
                    </p>
                )}
            </div>
        </div>
    );
}
