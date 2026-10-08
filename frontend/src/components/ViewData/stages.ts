export type Stage = "Regular" | "Playoffs" | "Preseason";

export const STAGES: Stage[] = ["Regular", "Playoffs", "Preseason"];

/** The label the pickers show, to the season_type every endpoint expects. */
export const STAGE_TO_SEASON_TYPE: Record<Stage, string> = {
    Regular: "regular",
    Playoffs: "playoffs",
    Preseason: "preseason",
};
