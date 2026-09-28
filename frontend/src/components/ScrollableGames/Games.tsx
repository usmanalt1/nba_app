import { useEffect, useState } from 'react';
import { GamesInfo, type LatestGame } from './GamesInfo';
import { apiFetch } from '../../lib/api';
import { env } from '../../env';

export function Games() {
  const [games, setGames] = useState<LatestGame[]>([]);

  useEffect(() => {
    const { VITE_DEFAULT_SEASON: season, VITE_DEFAULT_SEASON_TYPE: season_type } = env;
    apiFetch(`/api/nba/db/get_latest_games/season=${season}/season_type=${season_type}`)
      .then(r => r.json())
      .then(data => setGames(Array.isArray(data) ? data : []))
      .catch(() => setGames([]));
  }, []);

  if (games.length === 0) {
    return <div style={{ fontSize: 13, color: 'var(--paper-faint)', padding: '8px 0' }}>No recent games.</div>;
  }

  return (
    <div className="rail">
      <div style={{ display: 'flex', gap: 14, width: 'max-content' }}>
        {games.map((game, index) => (
          <div
            key={game.game_id ?? index}
            style={{
              minWidth: 268,
              backgroundColor: 'var(--panel)',
              border: '1px solid var(--line)',
              borderRadius: 4,
              padding: '14px 18px',
              color: 'var(--paper)',
            }}
          >
            <GamesInfo {...game} />
          </div>
        ))}
      </div>
    </div>
  );
}
