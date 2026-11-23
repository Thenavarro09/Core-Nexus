export type SqlAuth = 'windows' | 'sql'

export type ConnectionTestRequest = {
  server: string
  port: number
  database: string
  auth: SqlAuth
  username: string
  password: string
  driver: string
  trust_server_certificate: boolean
}

export type DatabaseInfo = {
  name: string
  database_id: number
  state: string
  recovery_model: string
  create_date: string | null
}

export type ConnectionTestResponse = {
  ok: boolean
  server_name: string
  version: string
  current_database: string
  databases: DatabaseInfo[]
}

export type ApiErrorBody = {
  detail?: string
  code?: string
}
