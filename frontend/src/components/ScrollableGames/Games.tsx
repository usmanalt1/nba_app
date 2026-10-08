import { useEffect, useState } from 'react';
import { GamesInfo, type LatestGame } from './GamesInfo';
import { apiFetch } from '../../lib/api';
import { BoxScore } from './BoxScore';
import { env } from '../../env';

interface GamesProps {
  /** null while the caller resolves it, which holds the fetch */
  season?: string | null;
}

export function Games({ season }: GamesProps = {}) {
  const [games, setGames] = useState<LatestGame[]>([]);
  const [openGameId, setOpenGameId] = useState<string | null>(null);
  const seasonName = season ?? env.VITE_DEFAULT_SEASON;

  useEffect(() => {
    if (!seasonName) return;
    const seasonType = env.VITE_DEFAULT_SEASON_TYPE ?? 'regular';
    apiFetch(`/api/nba/db/get_latest_games/season=${seasonName}/season_type=${seasonType}`)
      .then(r => r.json())
      .then(data => setGames(Array.isArray(data) ? data : []))
      .catch(() => setGames([]));
  }, [seasonName]);

  if (games.length === 0) {
    return <div style={{ fontSize: 13, color: 'var(--paper-faint)', padding: '8px 0' }}>No recent games.</div>;
  }

  return (
    <>
      <div className="rail">
        <div style={{ display: 'flex', gap: 14, width: 'max-content' }}>
          {games.map((game, index) => (
            <button
              key={game.game_id ?? index}
              type="button"
              onClick={() => game.game_id && setOpenGameId(game.game_id)}
              disabled={!game.game_id}
              title={game.game_id ? 'View box score' : undefined}
              style={{
                minWidth: 268,
                backgroundColor: 'var(--panel)',
                border: '1px solid var(--line)',
                borderRadius: 4,
                padding: '14px 18px',
                color: 'var(--paper)',
                textAlign: 'left',
                font: 'inherit',
                cursor: game.game_id ? 'pointer' : 'default',
              }}
            >
              <GamesInfo {...game} />
            </button>
          ))}
        </div>
      </div>
      <BoxScore gameId={openGameId} onClose={() => setOpenGameId(null)} />
    </>
  );
}
