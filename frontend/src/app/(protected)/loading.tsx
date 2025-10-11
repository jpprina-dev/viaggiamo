export default function ProtectedLoading() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-emerald-50 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-primary-600 mx-auto mb-4"></div>
        <p className="text-gray-600 font-medium">Cargando...</p>
      </div>
    </div>
  )
}
