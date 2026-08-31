export function parseAwayTeam(matchup: string, homeTeam: string): string {
    return matchup.replace(`${homeTeam} vs `, '').trim();
}
