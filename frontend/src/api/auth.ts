import { api } from './client'
import type { LoginResponse, User } from './types'

export const login = (username: string, password: string) =>
  api.post<LoginResponse>('/auth/login', { username, password })

export const fetchMe = () => api.get<User>('/auth/me')
