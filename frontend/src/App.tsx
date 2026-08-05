import { BrowserRouter as Router, Routes, Route} from 'react-router-dom';
import {useState} from 'react';
import { MantineProvider } from '@mantine/core';
import '@mantine/core/styles.css'; // don't forget this, classic gotcha
import { Navbar } from './components/Navbar/MatineNavbar';
import { Home } from './components/Home/Home';
import { Predictions } from './components/Predictions/Predictions';
import { ViewDataPage } from './components/ViewData/ViewDataPage';
import { theme } from './theme';



function App() {
  const [activeTab, setActiveTab] = useState('standings');

  return (
    <MantineProvider theme={theme} defaultColorScheme="dark">
      <Router>
        <div style={{ display: 'flex', height: '100vh' }}>
          <Navbar />
          <div style={{ flex: 1, padding: '20px', minWidth: 0 }}>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/view" element={<ViewDataPage />}/>
              <Route
                path="/predictions"
                element={<Predictions activeTab={activeTab} setActiveTab={setActiveTab} />}
              />
            </Routes>
          </div>

        </div>
      </Router>
    </MantineProvider>
  )
}

export default App
