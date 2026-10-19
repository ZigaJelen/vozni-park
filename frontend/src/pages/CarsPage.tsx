import { keepPreviousData, useQuery } from '@tanstack/react-query'
import { useEffect, useState } from 'react'
import { Alert, Button, Pagination, Spinner } from 'react-bootstrap'
import { useTranslation } from 'react-i18next'
import { Link, useSearchParams } from 'react-router'
import { fetchBrands, fetchCars } from '../api/cars'
import { errorMessage } from '../api/client'
import type { Car, CarListParams, SortField } from '../api/types'
import { useAuth } from '../auth/useAuth'
import CarFilters from '../components/CarFilters'
import CarsTable from '../components/CarsTable'
import DeleteCarModal from '../components/DeleteCarModal'

const SORT_FIELDS: SortField[] = ['id', 'brand', 'year', 'price']
const DEFAULT_PARAMS: CarListParams = { brand: '', price_min: '', price_max: '', sort: 'id', order: 'asc', page: 1 }

// Parametre seznama beremo iz naslova (npr. ?brand=Audi&sort=price&page=2),
// zato jih je mogoče deliti, osvežiti in uporabljati s tipko nazaj.
function readParams(search: URLSearchParams): CarListParams {
  const sort = search.get('sort') as SortField
  const page = Number(search.get('page'))
  return {
    brand: search.get('brand') ?? '',
    price_min: search.get('price_min') ?? '',
    price_max: search.get('price_max') ?? '',
    sort: SORT_FIELDS.includes(sort) ? sort : DEFAULT_PARAMS.sort,
    order: search.get('order') === 'desc' ? 'desc' : 'asc',
    page: Number.isInteger(page) && page > 0 ? page : 1,
  }
}

// V naslov zapišemo samo vrednosti, ki se razlikujejo od privzetih.
function writeParams(params: CarListParams): URLSearchParams {
  const search = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value !== DEFAULT_PARAMS[key as keyof CarListParams]) search.set(key, String(value))
  }
  return search
}

// Številke strani okoli trenutne (največ 5)
function pageNumbers(current: number, total: number): number[] {
  const start = Math.max(1, Math.min(current - 2, total - 4))
  const end = Math.min(total, start + 4)
  return Array.from({ length: end - start + 1 }, (_, index) => start + index)
}

export default function CarsPage() {
  const { t } = useTranslation()
  const { user } = useAuth()
  const isAdmin = user?.is_admin === true
  const [searchParams, setSearchParams] = useSearchParams()
  const [carToDelete, setCarToDelete] = useState<Car | null>(null)
  const params = readParams(searchParams)

  const cars = useQuery({
    queryKey: ['cars', params],
    queryFn: () => fetchCars(params),
    placeholderData: keepPreviousData,
  })
  const brands = useQuery({ queryKey: ['brands'], queryFn: fetchBrands })

  const update = (changes: Partial<CarListParams>) => setSearchParams(writeParams({ ...params, ...changes }))

  // Stran izven obsega (npr. ročno vpisan naslov ali izbrisan zadnji avtomobil na strani):
  // skoči na zadnjo stran.
  const lastPage = cars.data?.pages ?? 0
  useEffect(() => {
    if (!cars.isPlaceholderData && lastPage > 0 && params.page > lastPage) update({ page: lastPage })
  }, [cars.isPlaceholderData, lastPage, params.page])

  // Klik na isti stolpec obrne vrstni red, klik na drug stolpec ga razvrsti naraščajoče.
  const handleSort = (field: SortField) =>
    update({ sort: field, order: params.sort === field && params.order === 'asc' ? 'desc' : 'asc', page: 1 })

  const data = cars.data
  const from = data ? (data.page - 1) * data.per_page + 1 : 0

  return (
    <>
      <div className="d-flex justify-content-between align-items-center mb-3">
        <h1 className="h3 mb-0">{t('cars.title')}</h1>
        {isAdmin && (
          <Link to="/cars/new" className="btn btn-primary">
            {t('cars.actions.add')}
          </Link>
        )}
      </div>

      <CarFilters
        key={searchParams.toString()}
        values={params}
        brands={brands.data ?? []}
        onApply={(filters) => update({ ...filters, page: 1 })}
        onReset={() => setSearchParams({})}
      />

      {cars.isError && (
        <Alert variant="danger" className="d-flex justify-content-between align-items-center">
          {errorMessage(cars.error, t)}
          <Button size="sm" variant="outline-danger" onClick={() => cars.refetch()}>
            {t('common.retry')}
          </Button>
        </Alert>
      )}

      {cars.isPending && (
        <Spinner animation="border" role="status">
          <span className="visually-hidden">{t('common.loading')}</span>
        </Spinner>
      )}

      {data && data.total === 0 && <p className="text-muted">{t('cars.empty')}</p>}

      {data && data.total > 0 && (
        <>
          <CarsTable
            cars={data.items}
            sort={params.sort}
            order={params.order}
            dimmed={cars.isPlaceholderData}
            isAdmin={isAdmin}
            onSort={handleSort}
            onDelete={setCarToDelete}
          />
          <div className="d-flex flex-column flex-md-row justify-content-between align-items-center gap-2">
            <small className="text-muted">
              {t('cars.showing', { from, to: from + data.items.length - 1, total: data.total })}
            </small>
            {data.pages > 1 && (
              <Pagination className="mb-0">
                <Pagination.Item
                  aria-label={t('pagination.previous')}
                  disabled={data.page <= 1}
                  onClick={() => update({ page: data.page - 1 })}
                >
                  ‹
                </Pagination.Item>
                {pageNumbers(data.page, data.pages).map((number) => (
                  <Pagination.Item
                    key={number}
                    active={number === data.page}
                    activeLabel={t('pagination.current')}
                    onClick={() => update({ page: number })}
                  >
                    {number}
                  </Pagination.Item>
                ))}
                <Pagination.Item
                  aria-label={t('pagination.next')}
                  disabled={data.page >= data.pages}
                  onClick={() => update({ page: data.page + 1 })}
                >
                  ›
                </Pagination.Item>
              </Pagination>
            )}
          </div>
        </>
      )}

      {isAdmin && carToDelete && <DeleteCarModal car={carToDelete} onClose={() => setCarToDelete(null)} />}
    </>
  )
}
