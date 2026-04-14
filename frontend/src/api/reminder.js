import request from './request'

export function getReminders(params) {
  return request.get('/reminders/list/', { params })
}

export function getPendingReminders() {
  return request.get('/reminders/list/pending/')
}

export function getUpcomingReminders() {
  return request.get('/reminders/list/upcoming/')
}

export function createReminder(data) {
  return request.post('/reminders/list/', data)
}

export function handleReminder(id) {
  return request.post(`/reminders/list/${id}/handle/`)
}

export function ignoreReminder(id) {
  return request.post(`/reminders/list/${id}/ignore/`)
}
