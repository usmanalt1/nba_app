import { Tabs } from '@mantine/core';
import { useState } from 'react';
import HomePlayerStats from "./HomePlayerStats";
import type { PlayerStats } from '../../types/player';


export default function HomeTabs() {
  const [activeTab, setActiveTab] = useState('player-stats');
  const [selectedPlayer, setSelectedPlayer] = useState<string | null>(null);
  const [selectedTeam, setSelectedTeam] = useState<string | null>(null);
  const [selectedSeason, setSelectedSeason] = useState<string | null>(null);
  const [rows, setRows] = useState<PlayerStats[]>([]);


  const typeTypes = [
    { value: 'player-stats', label: 'Player Stats' },
    { value: 'team-stats', label: 'Team Stats' },
    { value: 'season-stats', label: 'Season Stats' },
    { value: 'advanced-stats', label: 'Advanced Stats' }
  ];

  const onClickTab = (value: string) => {
    setActiveTab(value);
  }

  return (
    <><Tabs variant="pills" style={{ width: "100%", marginBottom: '30px' }} defaultValue="player-stats">
      <Tabs.List grow={true} style={{ width: "100%", display: 'flex', justifyContent: 'space-between' }}>
        {typeTypes.map(type =>
          <Tabs.Tab
            onClick={() => onClickTab(type.value)} value={type.value} style={{ fontWeight: 700, fontSize: '16px' }}>
            {type.label}
          </Tabs.Tab>
        )}
      </Tabs.List>
    </Tabs>
      {activeTab === 'player-stats' && <HomePlayerStats
        selectedPlayer={selectedPlayer}
        selectedTeam={selectedTeam}
        selectedSeason={selectedSeason}
        rows={rows}
        setSelectedPlayer={setSelectedPlayer}
        setSelectedTeam={setSelectedTeam}
        setSelectedSeason={setSelectedSeason}
        setRows={setRows}
      />}
    </>
  );
}