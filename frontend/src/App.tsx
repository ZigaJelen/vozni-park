import { Container } from 'react-bootstrap'
import { Route, Routes } from 'react-router'
import RequireAdmin from './auth/RequireAdmin'
import AppNavbar from './components/AppNavbar'
import CarFormPage from './pages/CarFormPage'
import CarsPage from './pages/CarsPage'
import LoginPage from './pages/LoginPage'
import NotFoundPage from './pages/NotFoundPage'

export default function App() {
  return (
    <>
      <AppNavbar />
      <Container className="py-4">
        <Routes>
          <Route path="/" element={<CarsPage />} />
          <Route path="/login" element={<LoginPage />} />
          {/* Dodajanje in urejanje je dovoljeno samo prijavljenemu administratorju */}
          <Route element={<RequireAdmin />}>
            <Route path="/cars/new" element={<CarFormPage />} />
            <Route path="/cars/:id/edit" element={<CarFormPage />} />
          </Route>
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Container>
    </>
  )
}
