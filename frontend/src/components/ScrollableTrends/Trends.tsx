import { Box, Group } from '@mantine/core';
import { useEffect, useState } from 'react';
import {Helper} from './Helper';

export function Trends() {
  const [playersPoints, setPlayersPoints] = useState([]);
  const [playersRebounds, setPlayersRebounds] = useState([]);
  const [playersAssists, setPlayersAssists] = useState([]);
  const [playersPlusMinus, setPlayersPlusMinus] = useState([]);


  useEffect(() => {
    fetch(`/api/nba/db/get_top_3_best_players_latest_season/points`)
        .then(r => r.json())
        .then(setPlayersPoints);
    fetch(`/api/nba/db/get_top_3_best_players_latest_season/rebounds`)
        .then(r => r.json())
        .then(setPlayersRebounds);
    fetch(`/api/nba/db/get_top_3_best_players_latest_season/assists`)
        .then(r => r.json())
        .then(setPlayersAssists);
    fetch(`/api/nba/db/get_top_3_best_players_latest_season/plus_minus`)
        .then(r => r.json())
        .then(setPlayersPlusMinus);
  }, []);

  
  const HelperPoints = Helper(playersPoints, 'average_points');
  const HelperRebounds = Helper(playersRebounds, 'average_rebounds');
  const HelperAssists = Helper(playersAssists, 'average_assists');
  const HelperPlusMinus = Helper(playersPlusMinus, 'average_plus_minus');
  return (
    <Box>
        <Group wrap="nowrap" gap="md">
          {Array.from({ length: 4 }).map((_, index) => (
            <Box
              key={index}
              style={{
                minWidth: 350,
                height: 120,
                backgroundColor: 'var(--panel)',
                border: '1px solid var(--line)',
                borderRadius: 4,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'var(--paper)',
                fontWeight: 500,
              }}
            >
                <div style={{ textAlign: 'center', fontSize: '14px', padding: '10px' }}>
                    {index === 0 ? HelperPoints : index == 1 ? HelperRebounds : index == 2 ? HelperAssists : index == 3 ? HelperPlusMinus : 'Loading...'}
                </div>
            </Box>
          ))}
        </Group>
    </Box>
  );
}