import { Select } from '@mantine/core';
import { useState } from 'react';

export function Home() {

    const [season, setSeason] = useState('2025-26')

    const handleSeasonChange = (value: string) => {
        setSeason(value);
    }
  return (
    <div style={{ padding: '20px' }}>
      <h1>Welcome to the NBA Data App</h1>
      <p>
        This application allows you to collect, view, and analyze NBA data. Use the navigation links to explore the features of the app.
      </p>
        <div style={{ marginTop: '20px', display: 'flex', flexDirection: 'row', gap: '30px' }}>
            <div style={{ marginBottom: '10px', width: '300px' }}>
                <Select
                label="Season"
                placeholder="Pick one"
                data={[
                    { value: 'lakers', label: 'Los Angeles Lakers' },
                    { value: 'warriors', label: 'Golden State Warriors' },
                    { value: 'nets', label: 'Brooklyn Nets' },
                    { value: 'bucks', label: 'Milwaukee Bucks' },
                ]}
                value={season}
                onChange={handleSeasonChange}
                />
            </div>
            <div style={{ marginBottom: '10px', width: '300px' }}>
                <Select
                label="Data Type"
                placeholder="Pick one"
                data={[
                    { value: 'roster', label: 'Team Roster' },
                    { value: 'stats', label: 'Player Stats' },
                    { value: 'schedule', label: 'Team Schedule' },
                ]}
                />
            </div>
        </div>
    </div>
  );
}