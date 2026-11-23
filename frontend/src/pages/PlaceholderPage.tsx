type PlaceholderPageProps = {
  title: string
  description: string
}

export function PlaceholderPage({ title, description }: PlaceholderPageProps) {
  return (
    <section className="page">
      <header className="page-header">
        <h1>{title}</h1>
        <p>{description}</p>
      </header>
      <div className="empty-state">
        <h2>Módulo pendiente</h2>
        <p>
          Esta sección ya tiene su lugar en la aplicación. El contenido se
          agregará en el siguiente paso del proyecto.
        </p>
      </div>
    </section>
  )
}
