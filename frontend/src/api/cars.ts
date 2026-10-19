import { api } from './client'
import type { Car, CarInput, CarList, CarListParams } from './types'

// GET /api/cars: prazni filtri se ne pošljejo
export function fetchCars(params: CarListParams) {
  const query = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value !== '') query.set(key, String(value))
  }
  return api.get<CarList>(`/cars?${query}`)
}

export const fetchBrands = () => api.get<string[]>('/brands')

export const fetchCar = (id: string) => api.get<Car>(`/cars/${id}`)

// POST, PUT in DELETE zahtevajo administratorja
export const createCar = (input: CarInput) => api.post<Car>('/cars', input)
export const updateCar = (id: number, input: CarInput) => api.put<Car>(`/cars/${id}`, input)
export const deleteCar = (id: number) => api.delete(`/cars/${id}`)
