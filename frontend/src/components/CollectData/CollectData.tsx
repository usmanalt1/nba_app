import { Box } from "@mantine/core";

export function CollectData() {
    return (
        <div>
            <div style={{display: 'flex', gap: '10px', width: '100%'}}>
                <button style={{flex: 1, padding: '5px', fontSize: '14px', backgroundColor: '#007bff', color: 'white'}}>Collect Data</button>
                <button style={{flex: 1, padding: '5px', fontSize: '14px', backgroundColor: '#dc3545', color: 'white'}}>Stop Collection</button>
                <button style={{flex: 1, padding: '5px', fontSize: '14px', backgroundColor: '#28a745', color: 'white'}}>View Collected Data</button>
            </div>
                
            <Box style={{backgroundColor: '#f8f9fa', minHeight: '200px', display: 'flex', gap: '10px', alignItems: 'center'}}>
                <p>Collected Data Will Appear Here</p>
                <Box style={{backgroundColor: '#000', width: '10%', color: '#fff', flex:1, padding: '10px'}}>
                    Collected Data Will Appear Here
                </Box>
                <Box style={{backgroundColor: '#000', width: '10%', color: '#fff', flex:1, padding: '10px'}}>
                    Collected Data Will Appear Here
                </Box>
            </Box>
        </div>
    );
}