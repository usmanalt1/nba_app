import { useEffect } from 'react';
import { BrowserRouter as Router, Navigate, Routes, Route, useLocation } from 'react-router-dom';
import { MantineProvider } from '@mantine/core';
import '@mantine/core/styles.css'; // don't forget this, classic gotcha
import { Navbar } from './components/Navbar/MatineNavbar';
import { Home } from './components/Home/Home';
import { Predictions } from './components/Predictions/Predictions';
import { ViewDataPage } from './components/ViewData/ViewDataPage';
import { theme } from './theme';
import { NbaAi } from './components/NbaAi/NbaAi';
import { AuthPage } from './components/Auth/AuthPage';
import { clearSession, isAccessTokenExpired } from './lib/api';


function AppContent() {
  const location = useLocation();
  const accessToken = sessionStorage.getItem('access_token');
  const isExpired = accessToken ? isAccessTokenExpired(accessToken) : false;
  const isAuthenticated = Boolean(accessToken && !isExpired);

  useEffect(() => {
    if (isExpired) clearSession();
  }, [isExpired]);

  const routes = (
    <Routes>
      <Route path="/auth" element={<AuthPage />} />
      <Route path="/" element={<Home />} />
      <Route path="/view" element={<ViewDataPage />}/>
      <Route path="/predictions" element={<Predictions />} />
      <Route path="/nbai" element={<NbaAi />} />
    </Routes>
  );

  if (!isAuthenticated && location.pathname !== '/auth') {
    return <Navigate to="/auth" replace />;
  }

  if (isAuthenticated && location.pathname === '/auth') {
    return <Navigate to="/" replace />;
  }

  if (location.pathname === '/auth') {
    return routes;
  }

  return (
    <div style={{ display: 'flex', height: '100vh', overflow: 'hidden' }}>
      <Navbar />
      <div style={{ flex: 1, padding: '20px', minWidth: 0, height: '100vh', overflowY: 'auto', boxSizing: 'border-box' }}>
        {routes}
      </div>
    </div>
  );
}

function App() {
  return (
    <MantineProvider theme={theme} defaultColorScheme="dark">
      <Router>
        <AppContent />
      </Router>
    </MantineProvider>
  )
}

export default App
