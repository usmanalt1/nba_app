import { Games } from  "../ScrollableGames/Games";
import { HomeTrends } from "./HomeTrends";

export function Home() {
    return (
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
            <div style={{ marginBottom: '30px', width: '100%', display: 'flex', justifyContent: 'left' }}>
                <Games />
            </div>
            <HomeTrends />
            {/* <div style={{ marginBottom: '30px', width: '100%', display: 'flex', justifyContent: 'left' , gap: '30px', flexWrap: 'wrap' }}>
                <Box 
                    w={{ base: '100%', lg: 400 }} 
                    h={400} 
                    p="xl" 
                    bg="var(--panel)"
                    c="var(--paper)"
                    >
                    This is a large box!
                </Box>
                <Box 
                    w={{ base: '100%', lg: 400 }} 
                    h={400} 
                    p="xl" 
                    bg="var(--panel)"
                    c="var(--paper)"
                    >
                    This is a large box!
                </Box>
                <Box 
                    w={{ base: '100%', lg: 400 }} 
                    h={400} 
                    p="xl" 
                    bg="var(--panel)"
                    c="var(--paper)"
                    >
                    This is a large box!
                </Box>
            </div> */}
        </div>
    );
}