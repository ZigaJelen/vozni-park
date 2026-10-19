import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Alert, Button, Modal } from 'react-bootstrap'
import { useTranslation } from 'react-i18next'
import { deleteCar } from '../api/cars'
import { errorMessage } from '../api/client'
import type { Car } from '../api/types'

interface Props {
  car: Car
  onClose: () => void
}

// Okno za potrditev brisanja. Po uspešnem brisanju se seznam osveži.
export default function DeleteCarModal({ car, onClose }: Props) {
  const { t } = useTranslation()
  const queryClient = useQueryClient()

  const remove = useMutation({
    mutationFn: () => deleteCar(car.id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['cars'] })
      queryClient.invalidateQueries({ queryKey: ['brands'] })
      onClose()
    },
  })

  return (
    <Modal show onHide={onClose} centered>
      <Modal.Header closeButton closeLabel={t('common.close')}>
        <Modal.Title>{t('cars.delete.title')}</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        {remove.error && <Alert variant="danger">{errorMessage(remove.error, t)}</Alert>}
        {t('cars.delete.confirm', { brand: car.brand, model: car.model, year: car.year })}
      </Modal.Body>
      <Modal.Footer>
        <Button variant="outline-secondary" onClick={onClose}>
          {t('common.cancel')}
        </Button>
        <Button variant="danger" disabled={remove.isPending} onClick={() => remove.mutate()}>
          {t('cars.delete.submit')}
        </Button>
      </Modal.Footer>
    </Modal>
  )
}
