import { useTeam, type TeamColours, type TeamKey } from '../../context/TeamColoursProvider';

interface TeamChipProps {
    /** A team id, abbreviation or name - or a side from useTeamPair, which already
        carries the matchup swap. */
    team: TeamKey | TeamColours;
}

function isResolved(team: TeamKey | TeamColours): team is TeamColours {
    return typeof team === 'object' && team !== null;
}

export function TeamChip({ team }: TeamChipProps) {
    // The hook has to run either way, so a resolved team looks up null and ignores it.
    const looked = useTeam(isResolved(team) ? null : team);
    const resolved = isResolved(team) ? team : looked;
    const known = resolved?.known ?? false;

    return (
        <span
            className="kicker"
            title={resolved?.name ?? 'Unknown team'}
            style={{
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                width: 30,
                height: 20,
                flexShrink: 0,
                borderRadius: 2,
                fontWeight: 700,
                background: known && resolved ? resolved.colour : 'var(--panel-2)',
                color: known && resolved ? resolved.text : 'var(--paper-dim)',
                // Keeps an unknown chip reading as a chip, not a smudge on the panel.
                border: known ? '1px solid transparent' : '1px solid var(--line)',
                boxSizing: 'border-box',
            }}
        >
            {resolved?.abbr || '—'}
        </span>
    );
}
