import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { AdministrationPage } from './pages/AdministrationPage'
import { ConnectionsPage } from './pages/ConnectionsPage'
import { MonitoringPage } from './pages/MonitoringPage'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route index element={<Navigate to="/conexiones" replace />} />
          <Route path="conexiones" element={<ConnectionsPage />} />
          <Route path="monitoreo" element={<MonitoringPage />} />
          <Route path="administracion" element={<AdministrationPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
