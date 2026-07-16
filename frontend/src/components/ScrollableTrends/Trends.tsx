import { Box, Button, Group } from '@mantine/core';
import { useScroller } from '@mantine/hooks';
import { useEffect, useState } from 'react';
import { PointsLogo } from './PointsLogo';

export function Trends() {
  const scroller = useScroller();
  const [players, setPlayers] = useState([]);


  useEffect(() => {
    fetch(`/api/nba/db/get_top_3_best_players_latest_season/points`)
        .then(r => r.json())
        .then(setPlayers);
    }, []);

  const topPlayersContent = players.length > 0 ? (
    <div>
      <PointsLogo style={{ width: 30, height: 30 }} />
      {players.map((player: any, i: number) => (
        <div key={i} style={{ fontWeight: i === 0 ? 700 : 400 }}>
          {player.player_name} - {player.average_points} PPG
        </div>
      ))}
    </div>
  ) : 'Loading...';

  return (
    <Box>
        <Group wrap="nowrap" gap="md">
          {Array.from({ length: 5 }).map((_, index) => (
            <Box
              key={index}
              style={{
                minWidth: 280,
                height: 120,
                backgroundColor: 'var(--mantine-color-gray-1)',
                border: '1.5px solid var(--mantine-color-blue-4)',
                borderRadius: 'var(--mantine-radius-md)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--mantine-color-dark-7)',
                fontWeight: 500,
              }}
            >
                <div style={{ textAlign: 'center', fontSize: '14px', padding: '10px' }}>
                    {index === 0 ? topPlayersContent : `Box ${index + 1}`}
                </div>
            </Box>
          ))}
        </Group>
    </Box>
  );
}