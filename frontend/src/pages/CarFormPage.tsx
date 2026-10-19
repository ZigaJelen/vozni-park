import { useQuery } from '@tanstack/react-query'
import { Alert, Spinner } from 'react-bootstrap'
import { useTranslation } from 'react-i18next'
import { Link, useParams } from 'react-router'
import { fetchCar } from '../api/cars'
import { errorMessage } from '../api/client'
import CarForm from '../components/CarForm'

// Ista stran za dodajanje (/cars/new) in urejanje (/cars/:id/edit).
// Pri urejanju najprej naložimo avtomobil, nato prikažemo obrazec z njegovimi podatki.
export default function CarFormPage() {
  const { t } = useTranslation()
  const { id } = useParams()
  const car = useQuery({ queryKey: ['cars', id], queryFn: () => fetchCar(id!), enabled: id !== undefined })

  if (id === undefined) return <CarForm />

  if (car.isPending) {
    return (
      <Spinner animation="border" role="status">
        <span className="visually-hidden">{t('common.loading')}</span>
      </Spinner>
    )
  }
  if (car.isError) {
    return (
      <>
        <Alert variant="danger">{errorMessage(car.error, t)}</Alert>
        <Link to="/">{t('notFound.back')}</Link>
      </>
    )
  }
  return <CarForm key={car.data.id} car={car.data} />
}
