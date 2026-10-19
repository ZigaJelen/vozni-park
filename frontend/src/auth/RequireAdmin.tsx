import { Spinner } from 'react-bootstrap'
import { useTranslation } from 'react-i18next'
import { Navigate, Outlet, useLocation } from 'react-router'
import { useAuth } from './useAuth'

// Zaščita strani: spusti samo prijavljenega administratorja.
// Neprijavljen uporabnik gre na prijavo (in se nato vrne sem), drugi na seznam.
export default function RequireAdmin() {
  const { t } = useTranslation()
  const { user, loading } = useAuth()
  const location = useLocation()

  if (loading) {
    return (
      <Spinner animation="border" role="status">
        <span className="visually-hidden">{t('common.loading')}</span>
      </Spinner>
    )
  }
  if (!user) return <Navigate to="/login" state={{ from: location.pathname }} replace />
  if (!user.is_admin) return <Navigate to="/" replace />
  return <Outlet />
}
