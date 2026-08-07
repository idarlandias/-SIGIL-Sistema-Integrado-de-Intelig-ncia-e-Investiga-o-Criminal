import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import CasoDetalhePage from './pages/CasoDetalhePage';
import GrafoVinculosPage from './pages/GrafoVinculosPage';
import UploadEvidenciaPage from './pages/UploadEvidenciaPage';
import RotaProtegida from './components/RotaProtegida';
import Layout from './components/Layout';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route
          path="/"
          element={
            <RotaProtegida>
              <Layout />
            </RotaProtegida>
          }
        >
          <Route index element={<Navigate to="/casos" replace />} />
          <Route path="casos" element={<DashboardPage />} />
          <Route path="casos/:numero" element={<CasoDetalhePage />} />
          <Route path="grafo/:cpf" element={<GrafoVinculosPage />} />
          <Route path="evidencias/nova" element={<UploadEvidenciaPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
