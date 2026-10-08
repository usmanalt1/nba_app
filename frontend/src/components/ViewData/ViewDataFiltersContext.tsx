import { createContext, useContext, useState, type Dispatch, type ReactNode, type SetStateAction } from 'react';
import type { Stage } from './stages';

export type ViewMode = "Players" | "Teams";
export type StatSet = "Basic" | "Advanced";

interface ViewDataFilters {
    viewMode: ViewMode;
    setViewMode: Dispatch<SetStateAction<ViewMode>>;
    statSet: StatSet;
    setStatSet: Dispatch<SetStateAction<StatSet>>;
    selectedSeason: string | null;
    setSelectedSeason: Dispatch<SetStateAction<string | null>>;
    selectedTeam: string | null;
    setSelectedTeam: Dispatch<SetStateAction<string | null>>;
    selectedStage: Stage;
    setSelectedStage: Dispatch<SetStateAction<Stage>>;
    selectedPosition: string | null;
    setSelectedPosition: Dispatch<SetStateAction<string | null>>;
    playerQuery: string;
    setPlayerQuery: Dispatch<SetStateAction<string>>;
}

const ViewDataFiltersContext = createContext<ViewDataFilters | null>(null);

export function ViewDataFiltersProvider({ children }: { children: ReactNode }) {
    const [viewMode, setViewMode] = useState<ViewMode>("Players");
    const [statSet, setStatSet] = useState<StatSet>("Basic");
    const [selectedSeason, setSelectedSeason] = useState<string | null>(null);
    const [selectedTeam, setSelectedTeam] = useState<string | null>(null);
    const [selectedStage, setSelectedStage] = useState<Stage>("Regular");
    const [selectedPosition, setSelectedPosition] = useState<string | null>(null);
    const [playerQuery, setPlayerQuery] = useState("");

    return (
        <ViewDataFiltersContext.Provider
            value={{
                viewMode, setViewMode,
                statSet, setStatSet,
                selectedSeason, setSelectedSeason,
                selectedTeam, setSelectedTeam,
                selectedStage, setSelectedStage,
                selectedPosition, setSelectedPosition,
                playerQuery, setPlayerQuery,
            }}
        >
            {children}
        </ViewDataFiltersContext.Provider>
    );
}

export function useViewDataFilters() {
    const filters = useContext(ViewDataFiltersContext);
    if (!filters) {
        throw new Error("useViewDataFilters must be used inside a ViewDataFiltersProvider");
    }
    return filters;
}
