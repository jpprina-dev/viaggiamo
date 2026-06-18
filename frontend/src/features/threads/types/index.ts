/**
 * Types for the threads (1:1 chat) feature.
 */

import { z } from 'zod'

// ─── Enums ──────────────────────────────────────────────────────────────────

export const MessageKind = {
  user:   'user',
  system: 'system',
} as const
export type MessageKind = typeof MessageKind[keyof typeof MessageKind]

export const MessageEventType = {
  contactWarning:  'contact_warning',
  requestSent:     'request_sent',
  requestAccepted: 'request_accepted',
  requestRejected: 'request_rejected',
  requestRevoked:  'request_revoked',
} as const
export type MessageEventType = typeof MessageEventType[keyof typeof MessageEventType]

// ─── View models ────────────────────────────────────────────────────────────

export interface Thread {
  id: number
  tripId: number
  passengerUserId: number
  createdAt: string
  isClosed: boolean
}

export interface Message {
  id: number
  threadId: number
  kind: MessageKind
  senderId: number | null
  eventType: string | null
  body: string | null
  createdAt: string
}

// ─── Zod schemas ──────────────────────────────────────────────────────────────

export const threadSchema = z.object({
  id: z.number(),
  tripId: z.number(),
  passengerUserId: z.number(),
  createdAt: z.string(),
  isClosed: z.boolean(),
})

export const messageSchema = z.object({
  id: z.number(),
  threadId: z.number(),
  kind: z.enum(['user', 'system']),
  senderId: z.number().nullable(),
  eventType: z.string().nullable(),
  body: z.string().nullable(),
  createdAt: z.string(),
})
