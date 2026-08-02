function TeamRow({ name, pts, dotColor, won }: { name: string; pts: number; dotColor: string; won: boolean }) {
    return (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '3px 0', fontFamily: "'IBM Plex Mono', monospace", fontSize: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontWeight: won ? 600 : 400, color: won ? 'var(--gold)' : 'var(--paper)' }}>
                <span style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: dotColor, flexShrink: 0 }} />
                {name}
            </div>
            <div style={{ fontWeight: won ? 700 : 400, color: won ? 'var(--gold)' : 'var(--paper-dim)' }}>
                {pts}
            </div>
        </div>
    );
}

export function GamesInfo(games: any) {
    const homeWon = games.home_pts > games.away_pts;
    const date = new Date(games.game_date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' });

    return (
        <div>
            <div
                style={{
                    fontFamily: "'IBM Plex Mono', monospace",
                    fontSize: '8px',
                    letterSpacing: '0.04em',
                    color: 'var(--paper-dim)',
                    marginBottom: '10px'
                }}
            >
                {date}
            </div>
            <TeamRow name={games.home_team_name} pts={games.home_pts} dotColor="var(--home)" won={homeWon} />
            <TeamRow name={games.away_team_name} pts={games.away_pts} dotColor="var(--away)" won={!homeWon} />
        </div>
    );
}