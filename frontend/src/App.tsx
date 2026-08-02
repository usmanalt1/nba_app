import { BrowserRouter as Router, Routes, Route} from 'react-router-dom';
import {useState} from 'react';
import { MantineProvider } from '@mantine/core';
import '@mantine/core/styles.css'; // don't forget this, classic gotcha
import { Navbar } from './components/Navbar/MatineNavbar';
import { Home } from './components/Home/Home';
import { Predictions } from './components/Predictions/Predictions';
import type { TrainResponse } from './types/predictions';
import { theme } from './theme';


function App() {
  const [selectedModel, setSelectedModel] = useState<string | null>(null);
  const [selectedSeason, setSelectedSeason] = useState<string | null>(null);
  const [result, setResult] = useState<TrainResponse | null>(null);
  const [activeTab, setActiveTab] = useState('standings');

  return (
    <MantineProvider theme={theme} defaultColorScheme="dark">
      <Router>
        <div style={{ display: 'flex', height: '100vh' }}>
          <Navbar />
          <div style={{ flex: 1, padding: '20px' }}>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route
                path="/predictions"
                element={
                  <Predictions
                    selectedModel={selectedModel}
                    selectedSeason={selectedSeason}
                    result={result}
                    activeTab={activeTab}
                    setSelectedModel={setSelectedModel}
                    setSelectedSeason={setSelectedSeason}
                    setResult={setResult}
                    setActiveTab={setActiveTab}
                  />
                }
              />
            </Routes>
          </div>

        </div>
      </Router>
    </MantineProvider>
  )
}

export default App
