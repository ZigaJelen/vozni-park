import { Button, Table } from 'react-bootstrap'
import { useTranslation } from 'react-i18next'
import { Link } from 'react-router'
import type { Car, SortField, SortOrder } from '../api/types'

interface Props {
  cars: Car[]
  sort: SortField
  order: SortOrder
  dimmed: boolean // true, medtem ko se nalaga nova stran (prikazani so še stari podatki)
  isAdmin: boolean // administrator vidi gumba Uredi in Izbriši
  onSort: (field: SortField) => void
  onDelete: (car: Car) => void
}

// Tabela avtomobilov. Glave stolpcev znamka, letnik in cena so klikljive (sortiranje).
export default function CarsTable({ cars, sort, order, dimmed, isAdmin, onSort, onDelete }: Props) {
  const { t, i18n } = useTranslation()
  const money = new Intl.NumberFormat(i18n.resolvedLanguage, { style: 'currency', currency: 'EUR' })

  function sortableHeader(field: SortField, label: string) {
    const ariaSort = sort !== field ? 'none' : order === 'asc' ? 'ascending' : 'descending'
    return (
      <th role="button" aria-sort={ariaSort} className="text-nowrap user-select-none" onClick={() => onSort(field)}>
        {label} {sort === field && (order === 'asc' ? '▲' : '▼')}
      </th>
    )
  }

  return (
    <Table responsive hover className="align-middle" style={{ opacity: dimmed ? 0.5 : 1 }}>
      <thead>
        <tr>
          {sortableHeader('brand', t('cars.columns.brand'))}
          <th>{t('cars.columns.model')}</th>
          {sortableHeader('year', t('cars.columns.year'))}
          {sortableHeader('price', t('cars.columns.price'))}
          <th>{t('cars.columns.fuel')}</th>
          <th>{t('cars.columns.doors')}</th>
          <th className="d-none d-md-table-cell">{t('cars.columns.description')}</th>
          {isAdmin && <th />}
        </tr>
      </thead>
      <tbody>
        {cars.map((car) => (
          <tr key={car.id}>
            <td>{car.brand}</td>
            <td>{car.model}</td>
            <td>{car.year}</td>
            <td className="text-nowrap">{money.format(car.price)}</td>
            <td>{t(`fuel.${car.fuel_type}`)}</td>
            <td>{car.doors}</td>
            <td className="d-none d-md-table-cell text-muted small">{car.description}</td>
            {isAdmin && (
              <td className="text-nowrap text-end">
                <Link to={`/cars/${car.id}/edit`} className="btn btn-sm btn-outline-primary me-2">
                  {t('cars.actions.edit')}
                </Link>
                <Button size="sm" variant="outline-danger" onClick={() => onDelete(car)}>
                  {t('cars.actions.delete')}
                </Button>
              </td>
            )}
          </tr>
        ))}
      </tbody>
    </Table>
  )
}
