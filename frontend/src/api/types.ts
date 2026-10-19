// Oblike podatkov, ki jih vrača backend (glej backend/app/models.py in backend/app/routes/)

export interface User {
  id: number
  username: string
  is_admin: boolean
}

export interface LoginResponse {
  access_token: string
  user: User
}

// Napake po poljih, npr. { year: "Letnik mora biti celo število." }
export type FieldErrors = Record<string, string>

export const FUEL_TYPES = ['petrol', 'diesel', 'electric', 'hybrid', 'lpg'] as const
export type FuelType = (typeof FUEL_TYPES)[number]

export interface Car {
  id: number
  brand: string
  model: string
  year: number
  price: number
  fuel_type: FuelType
  doors: number
  description: string | null
}

// Telo zahtevka za dodajanje in urejanje avtomobila. Prazna številska polja pošljemo
// kot null; strežnik jih zavrne z napako pri ustreznem polju.
export interface CarInput {
  brand: string
  model: string
  year: number | null
  price: number | null
  fuel_type: string
  doors: number | null
  description: string
}

export interface CarList {
  items: Car[]
  page: number
  per_page: number
  total: number
  pages: number
}

export type SortField = 'id' | 'brand' | 'model' | 'year' | 'price'
export type SortOrder = 'asc' | 'desc'

// Parametri seznama (enaki kot poizvedbeni parametri GET /api/cars)
export interface CarListParams {
  brand: string
  price_min: string
  price_max: string
  sort: SortField
  order: SortOrder
  page: number
}
