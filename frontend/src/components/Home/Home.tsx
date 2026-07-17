import { Trends } from "../ScrollableTrends/Trends";
import HomeTabs from "./HomeTabs";

export function Home() {


    return (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
            <div style={{ marginBottom: '30px', width: '100%', display: 'flex', justifyContent: 'left' }}>
                <Trends />
            </div>
            <HomeTabs />
        </div>
    );
}