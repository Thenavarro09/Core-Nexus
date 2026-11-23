import type { ApiErrorBody, ConnectionTestRequest, ConnectionTestResponse } from './types'

export class ApiError extends Error {
  code: string
  status: number

  constructor(message: string, code: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.code = code
    this.status = status
  }
}

export async function testConnection(
  payload: ConnectionTestRequest,
): Promise<ConnectionTestResponse> {
  let response: Response
  try {
    response = await fetch('/api/connections/test', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
  } catch {
    throw new ApiError(
      'No se pudo contactar la API. Comprueba que el backend esté en ejecución.',
      'api_unreachable',
      0,
    )
  }

  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as ApiErrorBody
    throw new ApiError(
      body.detail ?? 'No se pudo probar la conexión.',
      body.code ?? 'request_failed',
      response.status,
    )
  }

  return (await response.json()) as ConnectionTestResponse
}
