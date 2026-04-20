import { BrowserRouter, Routes, Route } from 'react-router-dom';
import MainLayout from './components/layout/MainLayout';
import Dashboard from './pages/Dashboard';
import LiveFeed from './pages/LiveFeed';
import FraudAlerts from './pages/FraudAlerts';
import UserDetail from './pages/UserDetail';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<MainLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/live" element={<LiveFeed />} />
          <Route path="/alerts" element={<FraudAlerts />} />
          <Route path="/users" element={<UserDetail />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
