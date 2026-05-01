export default function Loading() {
  return (
    <div className="min-h-screen bg-white flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-primary-container mx-auto mb-4"></div>
        <p className="text-on-surface-variant font-medium">Cargando Viajamos...</p>
      </div>
    </div>
  )
}
