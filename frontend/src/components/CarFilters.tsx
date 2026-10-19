import { type SubmitEvent, useState } from 'react'
import { Button, Col, Form, Row } from 'react-bootstrap'
import { useTranslation } from 'react-i18next'
import type { CarListParams } from '../api/types'

type Filters = Pick<CarListParams, 'brand' | 'price_min' | 'price_max'>

interface Props {
  values: Filters // trenutni filtri iz naslova
  brands: string[]
  onApply: (filters: Filters) => void
  onReset: () => void
}

// Filtra po znamki in ceni. Vrednosti se uveljavijo šele ob pritisku na gumb.
export default function CarFilters({ values, brands, onApply, onReset }: Props) {
  const { t } = useTranslation()
  const [brand, setBrand] = useState(values.brand)
  const [priceMin, setPriceMin] = useState(values.price_min)
  const [priceMax, setPriceMax] = useState(values.price_max)

  function handleSubmit(event: SubmitEvent) {
    event.preventDefault()
    onApply({ brand, price_min: priceMin.trim(), price_max: priceMax.trim() })
  }

  return (
    <Form onSubmit={handleSubmit} className="mb-3">
      <Row className="g-2 align-items-end">
        <Form.Group as={Col} xs={12} md={4} controlId="filter-brand">
          <Form.Label>{t('cars.filters.brand')}</Form.Label>
          <Form.Select value={brand} onChange={(event) => setBrand(event.target.value)}>
            <option value="">{t('cars.filters.allBrands')}</option>
            {brands.map((name) => (
              <option key={name} value={name}>
                {name}
              </option>
            ))}
          </Form.Select>
        </Form.Group>
        <Form.Group as={Col} xs={6} md={2} controlId="filter-price-min">
          <Form.Label>{t('cars.filters.priceMin')}</Form.Label>
          <Form.Control
            type="number"
            min={0}
            step="any"
            value={priceMin}
            onChange={(event) => setPriceMin(event.target.value)}
          />
        </Form.Group>
        <Form.Group as={Col} xs={6} md={2} controlId="filter-price-max">
          <Form.Label>{t('cars.filters.priceMax')}</Form.Label>
          <Form.Control
            type="number"
            min={0}
            step="any"
            value={priceMax}
            onChange={(event) => setPriceMax(event.target.value)}
          />
        </Form.Group>
        <Col xs={12} md="auto" className="d-flex gap-2">
          <Button type="submit">{t('cars.filters.apply')}</Button>
          <Button variant="outline-secondary" onClick={onReset}>
            {t('cars.filters.reset')}
          </Button>
        </Col>
      </Row>
    </Form>
  )
}
