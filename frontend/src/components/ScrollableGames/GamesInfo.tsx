import { TeamChip } from '../ui/TeamChip';
import { useTeamPair, type TeamColours } from '../../context/TeamColoursProvider';

interface TeamRowProps {
    name: string;
    pts: number;
    colours: TeamColours;
    won: boolean;
}

function TeamRow({ name, pts, colours, won }: TeamRowProps) {
    return (
        <div
            style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                padding: '4px 0',
                fontFamily: 'var(--mono)',
                fontSize: 13,
            }}
        >
            <div
                style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 10,
                    minWidth: 0,
                    fontWeight: won ? 600 : 400,
                    color: won ? 'var(--paper)' : 'var(--paper-dim)',
                }}
            >
                <TeamChip team={colours} />
                <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={name}>
                    {name}
                </span>
            </div>
            <div
                style={{
                    fontWeight: won ? 700 : 400,
                    color: won ? 'var(--paper)' : 'var(--paper-dim)',
                    fontVariantNumeric: 'tabular-nums',
                    paddingLeft: 10,
                }}
            >
                {pts}
            </div>
        </div>
    );
}

export interface LatestGame {
    game_id?: string;
    game_date: string;
    home_team_name: string;
    away_team_name: string;
    home_pts: number;
    away_pts: number;
}

export function GamesInfo({ game_date, home_team_name, away_team_name, home_pts, away_pts }: LatestGame) {
    const homeWon = home_pts > away_pts;
    const date = new Date(game_date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
    const { away, home } = useTeamPair(away_team_name, home_team_name);

    return (
        <div>
            <div className="kicker" style={{ marginBottom: 10 }}>{date} · Final</div>
            <TeamRow name={away_team_name} pts={away_pts} colours={away} won={!homeWon} />
            <TeamRow name={home_team_name} pts={home_pts} colours={home} won={homeWon} />
        </div>
    );
}
