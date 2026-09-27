import { Box, Group, ScrollArea } from '@mantine/core';
import { useEffect, useState } from 'react';
import { GamesInfo } from './GamesInfo';
import { apiFetch } from '../../lib/api';
import { env } from '../../env';

export function Games() {
    const [Games, setGames] = useState([]);

  useEffect(() => {
    const { VITE_DEFAULT_SEASON: season, VITE_DEFAULT_SEASON_TYPE: season_type } = env;
    apiFetch(`/api/nba/db/get_latest_games/season=${season}/season_type=${season_type}`)
      .then(r => r.json())
      .then(setGames);
  }, []);

  const length_games = Games.length

  return  (
    <ScrollArea scrollbars="x" type="always" w="100%" style={{ minWidth: 0 }}>
      <Box>
        <Group wrap="nowrap" gap="md">
          {Array.from({ length: length_games }).map((_, index) => (
            <Box
              key={index}
              style={{
                minWidth: 350,
                height: 110,
                backgroundColor: 'var(--panel)',
                border: '1px solid var(--line)',
                borderRadius: 4,
                padding: '14px 18px',
                color: 'var(--paper)',
              }}
            >
              {GamesInfo(Games[index])}
            </Box>
          ))}
        </Group>
      </Box>
    </ScrollArea>
  );








}