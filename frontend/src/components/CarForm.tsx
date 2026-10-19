import { useMutation, useQueryClient } from '@tanstack/react-query'
import { type ChangeEvent, type SubmitEvent, useState } from 'react'
import { Alert, Button, Col, Form, Row } from 'react-bootstrap'
import { useTranslation } from 'react-i18next'
import { Link, useNavigate } from 'react-router'
import { createCar, updateCar } from '../api/cars'
import { ApiError, errorMessage } from '../api/client'
import { type Car, type CarInput, FUEL_TYPES, type FieldErrors } from '../api/types'

interface Props {
  car?: Car // obstoječi avtomobil pri urejanju; pri dodajanju ga ni
}

// Vrednosti polj hranimo kot besedilo, v števila jih pretvorimo ob pošiljanju.
const toNumber = (text: string) => (text.trim() === '' ? null : Number(text))

type ControlElement = HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement

// Obrazec za dodajanje in urejanje avtomobila. Napake validacije prihajajo s strežnika po poljih.
export default function CarForm({ car }: Props) {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [values, setValues] = useState({
    brand: car?.brand ?? '',
    model: car?.model ?? '',
    year: car ? String(car.year) : '',
    price: car ? String(car.price) : '',
    fuel_type: car?.fuel_type ?? '',
    doors: car ? String(car.doors) : '',
    description: car?.description ?? '',
  })
  type FieldName = keyof typeof values

  const save = useMutation({
    mutationFn: (input: CarInput) => (car ? updateCar(car.id, input) : createCar(input)),
    onSuccess: () => {
      // Seznami in podrobnosti avtomobilov ter seznam znamk so zastareli
      queryClient.invalidateQueries({ queryKey: ['cars'] })
      queryClient.invalidateQueries({ queryKey: ['brands'] })
      navigate('/')
    },
  })

  // Napake validacije po poljih pokažemo ob poljih, druge napake nad obrazcem.
  const fieldErrors: FieldErrors = save.error instanceof ApiError ? save.error.fieldErrors : {}
  const showGeneralError = save.error !== null && Object.keys(fieldErrors).length === 0

  const setField = (name: FieldName) => (event: ChangeEvent<ControlElement>) => {
    const value = event.target.value
    setValues((current) => ({ ...current, [name]: value }))
  }

  function handleSubmit(event: SubmitEvent) {
    event.preventDefault()
    save.mutate({
      brand: values.brand.trim(),
      model: values.model.trim(),
      year: toNumber(values.year),
      price: toNumber(values.price),
      fuel_type: values.fuel_type,
      doors: toNumber(values.doors),
      description: values.description,
    })
  }

  // Polje z besedilom ali številom in sporočilom o napaki pod njim
  function inputField(name: FieldName, label: string, width: number, type = 'text') {
    return (
      <Form.Group as={Col} xs={12} md={width} controlId={name}>
        <Form.Label>{label}</Form.Label>
        <Form.Control
          type={type}
          step={type === 'number' ? 'any' : undefined}
          value={values[name]}
          onChange={setField(name)}
          isInvalid={name in fieldErrors}
          required
        />
        <Form.Control.Feedback type="invalid">{fieldErrors[name]}</Form.Control.Feedback>
      </Form.Group>
    )
  }

  return (
    <Form onSubmit={handleSubmit}>
      <h1 className="h3 mb-4">{car ? t('carForm.editTitle') : t('carForm.createTitle')}</h1>
      {showGeneralError && <Alert variant="danger">{errorMessage(save.error, t)}</Alert>}

      <Row className="g-3 mb-3">
        {inputField('brand', t('cars.columns.brand'), 6)}
        {inputField('model', t('cars.columns.model'), 6)}
        {inputField('year', t('cars.columns.year'), 3, 'number')}
        {inputField('price', t('carForm.price'), 3, 'number')}
        <Form.Group as={Col} xs={12} md={4} controlId="fuel_type">
          <Form.Label>{t('cars.columns.fuel')}</Form.Label>
          <Form.Select
            value={values.fuel_type}
            onChange={setField('fuel_type')}
            isInvalid={'fuel_type' in fieldErrors}
            required
          >
            <option value="">{t('carForm.choose')}</option>
            {FUEL_TYPES.map((fuel) => (
              <option key={fuel} value={fuel}>
                {t(`fuel.${fuel}`)}
              </option>
            ))}
          </Form.Select>
          <Form.Control.Feedback type="invalid">{fieldErrors.fuel_type}</Form.Control.Feedback>
        </Form.Group>
        {inputField('doors', t('cars.columns.doors'), 2, 'number')}
      </Row>

      <Form.Group className="mb-4" controlId="description">
        <Form.Label>{t('cars.columns.description')}</Form.Label>
        <Form.Control
          as="textarea"
          rows={3}
          value={values.description}
          onChange={setField('description')}
          isInvalid={'description' in fieldErrors}
        />
        <Form.Control.Feedback type="invalid">{fieldErrors.description}</Form.Control.Feedback>
      </Form.Group>

      <div className="d-flex gap-2">
        <Button type="submit" disabled={save.isPending}>
          {save.isPending ? t('carForm.saving') : t('carForm.save')}
        </Button>
        <Link to="/" className="btn btn-outline-secondary">
          {t('common.cancel')}
        </Link>
      </div>
    </Form>
  )
}
