import { BrowserRouter as Router} from 'react-router-dom';
import {useState} from 'react';
import { MantineProvider } from '@mantine/core';
import '@mantine/core/styles.css'; // don't forget this, classic gotcha
import { Navbar } from './components/Navbar/MatineNavbar';


function App() {
  
  const [data, setData] = useState("Something");

  const handleClick = async () => {
  console.log('Button clicked');
  const response = await fetch('/api/nba/collect/season/2024-25/1/team_roster=false');
  const data = await response.json();
  setData(data);
  console.log(data);
  console.log('API call successful');
};

  return (
    <MantineProvider>
      <Router>
        <div style={{ display: 'flex', height: '100vh' }}>
          <Navbar />
        </div>
      </Router>
    </MantineProvider>
  )
}

export default App
