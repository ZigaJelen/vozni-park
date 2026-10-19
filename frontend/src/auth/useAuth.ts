import { useQueryClient, useQuery } from '@tanstack/react-query'
import { fetchMe, login as apiLogin } from '../api/auth'
import { getToken, setToken } from '../api/client'

// Ključ v predpomnilniku, pod katerim je prijavljeni uporabnik (null, če nihče ni prijavljen)
export const ME_KEY = ['me']

// Stanje prijave. Prijavljeni uporabnik je podatek v predpomnilniku Queryja (ključ ME_KEY),
// zato Context ni potreben: vsaka komponenta, ki pokliče useAuth(), vidi isto stanje.
export function useAuth() {
  const queryClient = useQueryClient()
  // Če je shranjen žeton, ga preverimo z GET /auth/me (pri 401 ga klic API-ja sam izbriše).
  const { data: user = null, isLoading } = useQuery({
    queryKey: ME_KEY,
    queryFn: fetchMe,
    enabled: getToken() !== null,
    staleTime: Infinity,
  })

  async function login(username: string, password: string) {
    const data = await apiLogin(username, password)
    setToken(data.access_token)
    queryClient.setQueryData(ME_KEY, data.user)
  }

  function logout() {
    setToken(null)
    queryClient.setQueryData(ME_KEY, null)
  }

  return { user, loading: isLoading, login, logout }
}
