import { User, Bookmark, Search, PlusCircle, MessageCircle, type LucideIcon } from 'lucide-react'
import { ROUTES } from '@/config/routes'

export interface NavItem {
  id: string
  label: string
  icon: LucideIcon
  href: string
  disabled?: boolean
  badge?: string
}

export interface ProfileSubItem {
  label: string
  href: string
}

export const NAV_ITEMS: NavItem[] = [
  { id: 'profile',  label: 'Mi Perfil',     icon: User,          href: ROUTES.PROFILE },
  { id: 'my-trips', label: 'Mis Viajes',     icon: Bookmark,      href: ROUTES.BOOKINGS },
  { id: 'search',   label: 'Buscar Viajes',  icon: Search,        href: ROUTES.SEARCH },
  { id: 'publish',  label: 'Publicar Viaje', icon: PlusCircle,    href: ROUTES.TRIPS_CREATE },
  { id: 'chats',    label: 'Chats',          icon: MessageCircle, href: ROUTES.CHATS, disabled: true, badge: 'Próximamente' },
]

export const PROFILE_SUB_ITEMS: ProfileSubItem[] = [
  { label: 'Mi Perfil',       href: ROUTES.PROFILE },
  { label: 'Configuración',   href: ROUTES.SETTINGS },
  { label: 'Acerca de',       href: ROUTES.ABOUT },
  { label: 'Centro de Ayuda', href: ROUTES.HELP },
]
