import request from './request'

export function getCustomers(params) {
  return request.get('/customers/list/', { params })
}

export function getCustomer(id) {
  return request.get(`/customers/list/${id}/`)
}

export function createCustomer(data) {
  return request.post('/customers/list/', data)
}

export function updateCustomer(id, data) {
  return request.patch(`/customers/list/${id}/`, data)
}

export function deleteCustomer(id) {
  return request.delete(`/customers/list/${id}/`)
}

export function getCustomerStats() {
  return request.get('/customers/list/stats/')
}

export function getStores() {
  return request.get('/customers/stores/')
}

export function getTags() {
  return request.get('/customers/tags/')
}
