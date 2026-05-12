import { describe, it, expect } from 'vitest'
import { NAV_ITEMS, PROFILE_SUB_ITEMS } from '../navItems'
import { ROUTES } from '@/config/routes'

describe('NAV_ITEMS', () => {
  it('contains exactly 5 sections', () => {
    expect(NAV_ITEMS).toHaveLength(5)
  })

  it('is ordered: Mi Perfil, Mis Viajes, Buscar Viajes, Publicar Viaje, Chats', () => {
    expect(NAV_ITEMS.map(i => i.label)).toEqual([
      'Mi Perfil',
      'Mis Viajes',
      'Buscar Viajes',
      'Publicar Viaje',
      'Chats',
    ])
  })

  it('hrefs match ROUTES constants', () => {
    expect(NAV_ITEMS[0].href).toBe(ROUTES.PROFILE)
    expect(NAV_ITEMS[1].href).toBe(ROUTES.BOOKINGS)
    expect(NAV_ITEMS[2].href).toBe(ROUTES.SEARCH)
    expect(NAV_ITEMS[3].href).toBe(ROUTES.TRIPS_CREATE)
    expect(NAV_ITEMS[4].href).toBe(ROUTES.CHATS)
  })

  it('every item has an icon component', () => {
    NAV_ITEMS.forEach(item => expect(item.icon).toBeDefined())
  })

  it('shortLabels are the simplified versions', () => {
    expect(NAV_ITEMS.map(i => i.shortLabel)).toEqual([
      'Perfil',
      'Mis Viajes',
      'Buscar',
      'Publicar',
      'Chat',
    ])
  })

  it('Chats is disabled with badge "Próximamente"', () => {
    const chats = NAV_ITEMS.find(i => i.id === 'chats')
    expect(chats?.disabled).toBe(true)
    expect(chats?.badge).toBe('Próximamente')
  })
})

describe('PROFILE_SUB_ITEMS', () => {
  it('contains 4 items in order', () => {
    expect(PROFILE_SUB_ITEMS.map(i => i.label)).toEqual([
      'Mi Perfil',
      'Configuración',
      'Acerca de',
      'Centro de Ayuda',
    ])
  })

  it('hrefs match ROUTES constants', () => {
    expect(PROFILE_SUB_ITEMS[0].href).toBe(ROUTES.PROFILE)
    expect(PROFILE_SUB_ITEMS[1].href).toBe(ROUTES.SETTINGS)
    expect(PROFILE_SUB_ITEMS[2].href).toBe(ROUTES.ABOUT)
    expect(PROFILE_SUB_ITEMS[3].href).toBe(ROUTES.HELP)
  })
})
