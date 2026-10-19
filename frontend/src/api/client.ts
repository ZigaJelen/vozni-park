import type { TFunction } from 'i18next'
import { ME_KEY } from '../auth/useAuth'
import { queryClient } from '../queryClient'
import type { FieldErrors } from './types'

// Naslov API-ja se vgradi v JavaScript ob gradnji (VITE_API_URL)
const API_URL = import.meta.env.VITE_API_URL as string

const TOKEN_KEY = 'token'

// Žeton hranimo v localStorage, da prijava preživi osvežitev strani.
export const getToken = () => localStorage.getItem(TOKEN_KEY)
export const setToken = (token: string | null) =>
  token ? localStorage.setItem(TOKEN_KEY, token) : localStorage.removeItem(TOKEN_KEY)

// Napaka API-ja: koda HTTP (0, če strežnik ni dosegljiv), sporočilo in napake po poljih.
export class ApiError extends Error {
  status: number
  fieldErrors: FieldErrors

  constructor(status: number, message: string, fieldErrors: FieldErrors = {}) {
    super(message)
    this.status = status
    this.fieldErrors = fieldErrors
  }
}

export function errorMessage(error: unknown, t: TFunction): string {
  if (error instanceof ApiError) {
    if (error.status === 0) return t('errors.network')
    if (error.status === 401) return t('errors.sessionExpired')
    if (error.status === 403) return t('errors.forbidden')
    if (error.status === 404) return t('errors.notFound')
  }
  return t('errors.generic')
}

// Skupni klic API-ja: doda žeton, pošlje in prebere JSON, napake spremeni v ApiError.
async function send<T>(method: string, path: string, body?: unknown): Promise<T> {
  const token = getToken()
  const headers: Record<string, string> = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (token) headers.Authorization = `Bearer ${token}`

  let response: Response
  try {
    response = await fetch(`${API_URL}${path}`, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  } catch {
    throw new ApiError(0, 'Network error')
  }

  const data = response.status === 204 ? null : await response.json().catch(() => null)
  if (!response.ok) {
    // 401 pri prijavljenem uporabniku: žeton je potekel ali je neveljaven, zato ga odjavimo.
    if (response.status === 401 && token) {
      setToken(null)
      queryClient.setQueryData(ME_KEY, null)
    }
    throw new ApiError(response.status, data?.message ?? response.statusText, data?.errors)
  }
  return data as T
}

export const api = {
  get: <T>(path: string) => send<T>('GET', path),
  post: <T>(path: string, body: unknown) => send<T>('POST', path, body),
  put: <T>(path: string, body: unknown) => send<T>('PUT', path, body),
  delete: (path: string) => send<void>('DELETE', path),
}
