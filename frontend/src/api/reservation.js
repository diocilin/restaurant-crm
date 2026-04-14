import request from './request'

export function getReservations(params) {
  return request.get('/reservations/list/', { params })
}

export function getTodayReservations() {
  return request.get('/reservations/list/today/')
}

export function getReservationOverview(params) {
  return request.get('/reservations/list/overview/', { params })
}

export function getAvailableSeats(storeId, date) {
  return request.get('/reservations/list/available_seats/', { params: { store: storeId, date } })
}

export function getCalendarReservations(params) {
  return request.get('/reservations/list/calendar/', { params })
}

export function createReservation(data) {
  return request.post('/reservations/list/', data)
}

export function updateReservation(id, data) {
  return request.patch(`/reservations/list/${id}/`, data)
}

export function deleteReservation(id) {
  return request.delete(`/reservations/list/${id}/`)
}

export function confirmReservation(id) {
  return request.post(`/reservations/list/${id}/confirm/`)
}

export function cancelReservation(id) {
  return request.post(`/reservations/list/${id}/cancel/`)
}

export function arriveReservation(id) {
  return request.post(`/reservations/list/${id}/arrive/`)
}
