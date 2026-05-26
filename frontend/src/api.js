const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

async function parseResponse(response) {
  const contentType = response.headers.get('content-type') || ''
  const data = contentType.includes('application/json')
    ? await response.json()
    : await response.text()
  if (!response.ok) {
    const message = typeof data === 'string' ? data : data.detail || JSON.stringify(data)
    throw new Error(message)
  }
  return data
}

export async function getJson(path) {
  const response = await fetch(`${API_BASE}${path}`)
  return parseResponse(response)
}

export async function postJson(path, body) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  return parseResponse(response)
}

export async function deleteJson(path) {
  const response = await fetch(`${API_BASE}${path}`, { method: 'DELETE' })
  return parseResponse(response)
}

export async function postForm(path, formData) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    body: formData,
  })
  return parseResponse(response)
}

export { API_BASE }
