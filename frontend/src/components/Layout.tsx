import { NavLink, Outlet } from 'react-router-dom'

const links = [
  { to: '/conexiones', label: 'Conexiones' },
  { to: '/monitoreo', label: 'Monitoreo' },
  { to: '/administracion', label: 'Administración' },
]

export function Layout() {
  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-mark" aria-hidden="true">
            CN
          </span>
          <div>
            <strong>Core-Nexus</strong>
            <small>Administración SQL Server</small>
          </div>
        </div>
        <nav className="nav" aria-label="Módulos">
          {links.map((link) => (
            <NavLink key={link.to} to={link.to}>
              {link.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  )
}
