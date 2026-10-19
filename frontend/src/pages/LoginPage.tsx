import { useMutation } from '@tanstack/react-query'
import type { TFunction } from 'i18next'
import { type SubmitEvent, useState } from 'react'
import { Alert, Button, Col, Form, Row } from 'react-bootstrap'
import { useTranslation } from 'react-i18next'
import { Navigate, useLocation } from 'react-router'
import { ApiError } from '../api/client'
import { useAuth } from '../auth/useAuth'

function loginErrorMessage(error: Error, t: TFunction): string {
  if (error instanceof ApiError && error.status === 401) return t('login.invalid')
  if (error instanceof ApiError && error.status === 0) return t('errors.network')
  return t('errors.generic')
}

export default function LoginPage() {
  const { t } = useTranslation()
  const { user, login } = useAuth()
  const location = useLocation()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  // Prijava je mutacija: Query nam sam vodi stanje (isPending, error).
  const loginMutation = useMutation({
    mutationFn: (credentials: { username: string; password: string }) =>
      login(credentials.username, credentials.password),
  })

  // Po prijavi gremo tja, od koder nas je zaščitena stran poslala (privzeto na seznam).
  const from = (location.state as { from?: string } | null)?.from ?? '/'
  if (user) return <Navigate to={from} replace />

  function handleSubmit(event: SubmitEvent) {
    event.preventDefault()
    loginMutation.mutate({ username: username.trim(), password })
  }

  return (
    <Row className="justify-content-center">
      <Col md={6} lg={4}>
        <h1 className="h3 mb-4">{t('login.title')}</h1>
        {loginMutation.error && <Alert variant="danger">{loginErrorMessage(loginMutation.error, t)}</Alert>}
        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3" controlId="username">
            <Form.Label>{t('login.username')}</Form.Label>
            <Form.Control
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              autoComplete="username"
              required
              autoFocus
            />
          </Form.Group>
          <Form.Group className="mb-3" controlId="password">
            <Form.Label>{t('login.password')}</Form.Label>
            <Form.Control
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              autoComplete="current-password"
              required
            />
          </Form.Group>
          <Button type="submit" className="w-100" disabled={loginMutation.isPending}>
            {loginMutation.isPending ? t('login.submitting') : t('login.submit')}
          </Button>
        </Form>
      </Col>
    </Row>
  )
}
