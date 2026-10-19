import { QueryClient } from '@tanstack/react-query'

// Skupen QueryClient: uporabljata ga main.tsx (Provider) in api/client.ts (izven komponent).
export const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
