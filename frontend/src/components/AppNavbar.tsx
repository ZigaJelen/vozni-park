import { Button, ButtonGroup, Container, Nav, Navbar } from 'react-bootstrap'
import { useTranslation } from 'react-i18next'
import { Link, NavLink, useNavigate } from 'react-router'
import { useAuth } from '../auth/useAuth'
import { LANGUAGES } from '../i18n'

export default function AppNavbar() {
  const { t, i18n } = useTranslation()
  const { user, loading, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/')
  }

  return (
    <Navbar bg="light" data-bs-theme="light" expand="lg" >
      <Container>
        <Navbar.Brand as={Link} to="/">
          {t('app.title')}
        </Navbar.Brand>
        <Navbar.Toggle aria-controls="main-nav" />
        <Navbar.Collapse id="main-nav" className={"justify-content-end"}>
          <Nav className="mb-auto align-items-sm-center gap-2">
            <ButtonGroup size="sm" aria-label={t('nav.language')}>
              {LANGUAGES.map((lang) => (
                <Button
                  key={lang}
                  variant={i18n.resolvedLanguage === lang ? 'dark' : 'outline-dark'}
                  onClick={() => i18n.changeLanguage(lang)}
                >
                  {lang.toUpperCase()}
                </Button>
              ))}
            </ButtonGroup>
            {!loading &&
              (user ? (
                <>
                  <Navbar.Text>
                    {user.username}
                    {user.is_admin && ` (${t('nav.admin')})`}
                  </Navbar.Text>
                  <Button size="sm" variant="outline-dark" onClick={handleLogout}>
                    {t('nav.logout')}
                  </Button>
                </>
              ) : (
                <Nav.Link as={NavLink} to="/login">
                  {t('nav.login')}
                </Nav.Link>
              ))}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  )
}
