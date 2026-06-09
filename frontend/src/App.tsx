import { BrowserRouter as Router} from 'react-router-dom';
import {useState} from 'react';

import './App.css'

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
    <Router>
      <div>
        <h1>NBA</h1>
        <button onClick={handleClick}>Run Api</button>
        {data}
      </div>
    </Router>
  )
}

export default App
