import request from './request'

export function login(username, password) {
  return request.post('/token/', { username, password })
}

export function refreshToken(refresh) {
  return request.post('/token/refresh/', { refresh })
}

export function getUserInfo() {
  return request.get('/auth/me/')
}
