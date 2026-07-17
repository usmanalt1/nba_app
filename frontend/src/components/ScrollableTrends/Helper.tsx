import { PointsLogo, ReboundsLogo, AssistsLogo, PlusMinusLogo} from './Logos';

export function Helper(playerStats: any, statType: string) {

    const logos: { [key: string]: React.ReactNode } = {
        'average_points': <PointsLogo style={{ width: 30, height: 30 }} />,
        'average_rebounds': <ReboundsLogo style={{ width: 30, height: 30 }} />,
        'average_assists': <AssistsLogo style={{ width: 30, height: 30 }} />,
        'average_plus_minus': <PlusMinusLogo style={{ width: 30, height: 30 }} />,
    }

    const logo = logos[statType] ?? null;
    
    return playerStats.length > 0 ? (
        <div>
            {logo}
            {playerStats.map((player: any, i: number) => (
                <div key={i} style={{ fontWeight: i === 0 ? 700 : 400 }}>
                    {player.player_name} - {player[statType]} {statType === 'average_points' ? 'PPG' : statType === 'average_rebounds' ? 'RPG' : statType === 'average_assists' ? 'APG' : '+/-'}
                </div>
            ))}
        </div>
    ) : 'Loading...';


}