import { useState, type FormEvent } from 'react'
import { ApiError, testConnection } from '../api/client'
import type { ConnectionTestResponse, SqlAuth } from '../api/types'

const DEFAULT_DRIVER = 'ODBC Driver 18 for SQL Server'

type FormState = {
  server: string
  port: string
  database: string
  auth: SqlAuth
  username: string
  password: string
  driver: string
  trustServerCertificate: boolean
}

const initialForm: FormState = {
  server: 'localhost',
  port: '1433',
  database: 'master',
  auth: 'windows',
  username: '',
  password: '',
  driver: DEFAULT_DRIVER,
  trustServerCertificate: true,
}

export function ConnectionsPage() {
  const [form, setForm] = useState<FormState>(initialForm)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<ConnectionTestResponse | null>(null)

  function update<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((current) => ({ ...current, [key]: value }))
  }

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const port = Number(form.port)
    if (!Number.isInteger(port) || port < 1 || port > 65535) {
      setError('El puerto debe ser un número entre 1 y 65535.')
      setResult(null)
      return
    }

    setLoading(true)
    setError(null)
    try {
      const response = await testConnection({
        server: form.server.trim(),
        port,
        database: form.database.trim() || 'master',
        auth: form.auth,
        username: form.auth === 'sql' ? form.username : '',
        password: form.auth === 'sql' ? form.password : '',
        driver: form.driver.trim() || DEFAULT_DRIVER,
        trust_server_certificate: form.trustServerCertificate,
      })
      setResult(response)
    } catch (caught) {
      setResult(null)
      setError(
        caught instanceof ApiError
          ? caught.message
          : 'No se pudo probar la conexión.',
      )
    } finally {
      setLoading(false)
    }
  }

  const versionHeadline = result?.version.split('\n')[0] ?? ''

  return (
    <section className="page">
      <header className="page-header">
        <h1>Conexiones</h1>
        <p>
          Apunta a cualquier instancia de SQL Server. La base <code>master</code>{' '}
          sirve para ver el servidor completo; el esquema de prueba no está fijo.
        </p>
      </header>

      <div className="connection-layout">
        <form className="card" onSubmit={onSubmit}>
          <h2>Probar instancia</h2>
          <label>
            Servidor
            <input
              value={form.server}
              onChange={(event) => update('server', event.target.value)}
              autoComplete="off"
              required
            />
          </label>
          <div className="field-row">
            <label>
              Puerto
              <input
                value={form.port}
                onChange={(event) => update('port', event.target.value)}
                inputMode="numeric"
                required
              />
            </label>
            <label>
              Base de datos
              <input
                value={form.database}
                onChange={(event) => update('database', event.target.value)}
                autoComplete="off"
                required
              />
            </label>
          </div>
          <label>
            Autenticación
            <select
              value={form.auth}
              onChange={(event) => update('auth', event.target.value as SqlAuth)}
            >
              <option value="windows">Windows</option>
              <option value="sql">SQL Server</option>
            </select>
          </label>
          {form.auth === 'sql' && (
            <div className="field-row">
              <label>
                Usuario
                <input
                  value={form.username}
                  onChange={(event) => update('username', event.target.value)}
                  autoComplete="username"
                  required
                />
              </label>
              <label>
                Contraseña
                <input
                  type="password"
                  value={form.password}
                  onChange={(event) => update('password', event.target.value)}
                  autoComplete="current-password"
                />
              </label>
            </div>
          )}
          <details className="advanced">
            <summary>Opciones avanzadas</summary>
            <label>
              Controlador ODBC
              <input
                value={form.driver}
                onChange={(event) => update('driver', event.target.value)}
              />
            </label>
            <label className="checkbox">
              <input
                type="checkbox"
                checked={form.trustServerCertificate}
                onChange={(event) =>
                  update('trustServerCertificate', event.target.checked)
                }
              />
              Confiar en el certificado del servidor
            </label>
          </details>
          <button type="submit" disabled={loading}>
            {loading ? 'Conectando…' : 'Probar conexión'}
          </button>
        </form>

        <div className="card result-card">
          <h2>Resultado</h2>
          {error && (
            <p className="banner banner-error" role="alert">
              {error}
            </p>
          )}
          {!error && !result && (
            <p className="muted">
              Todavía no hay una prueba. La lista de bases aparece aquí cuando
              la instancia responde.
            </p>
          )}
          {result && (
            <>
              <dl className="facts">
                <div>
                  <dt>Servidor</dt>
                  <dd>{result.server_name}</dd>
                </div>
                <div>
                  <dt>Base actual</dt>
                  <dd>{result.current_database}</dd>
                </div>
                <div>
                  <dt>Versión</dt>
                  <dd>{versionHeadline}</dd>
                </div>
              </dl>
              <h3>Bases de la instancia</h3>
              <div className="table-wrap">
                <table>
                  <thead>
                    <tr>
                      <th>Nombre</th>
                      <th>Estado</th>
                      <th>Recuperación</th>
                      <th>Id</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.databases.map((database) => (
                      <tr key={database.database_id}>
                        <td>{database.name}</td>
                        <td>
                          <span className={stateClass(database.state)}>
                            {database.state}
                          </span>
                        </td>
                        <td>{database.recovery_model}</td>
                        <td>{database.database_id}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      </div>
    </section>
  )
}

function stateClass(state: string) {
  return state === 'ONLINE' ? 'state state-online' : 'state'
}
