import request from './request'

export function getDiningRecords(params) {
  return request.get('/dining/records/', { params })
}

export function createDiningRecord(data) {
  return request.post('/dining/records/', data)
}

export function updateDiningRecord(id, data) {
  return request.patch(`/dining/records/${id}/`, data)
}

export function deleteDiningRecord(id) {
  return request.delete(`/dining/records/${id}/`)
}
