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

export function importExcel(file, storeId) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('store', storeId)
  return request.post('/dining/records/import_excel/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export function getDishStats(params) {
  return request.get('/dining/records/dish_stats/', { params })
}

export function getImportLogs(params) {
  return request.get('/dining/records/import_logs/', { params })
}
