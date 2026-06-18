'use client'

import { useEffect, useRef } from 'react'
import { Loader2, MessagesSquare } from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'
import { useThread } from '../hooks/useThread'
import { useThreadPolling } from '../hooks/useThreadPolling'
import { MessageKind } from '../types'
import { MessageBubble } from './MessageBubble'
import { SystemMessage } from './SystemMessage'
import { MessageComposer } from './MessageComposer'

interface ThreadViewProps {
  tripId: number
  passengerUserId: number
}

export function ThreadView({ tripId, passengerUserId }: ThreadViewProps) {
  const { user } = useAuth()
  const { thread, loading: threadLoading, error: threadError } = useThread(tripId, passengerUserId)
  const threadId = thread?.id ?? null
  const { messages, loading: messagesLoading, refetch } = useThreadPolling(threadId)
  const scrollRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    const el = scrollRef.current
    if (el) el.scrollTop = el.scrollHeight
  }, [messages])

  const currentUserId = user?.id ?? -1
  const isClosed = thread?.isClosed ?? false

  if (threadLoading) {
    return (
      <div className="flex h-80 items-center justify-center text-on-surface-variant">
        <Loader2 className="h-6 w-6 animate-spin" aria-hidden="true" />
      </div>
    )
  }

  if (threadError || !thread) {
    return (
      <div className="flex h-80 flex-col items-center justify-center gap-2 px-6 text-center text-on-surface-variant">
        <MessagesSquare className="h-8 w-8 opacity-60" aria-hidden="true" />
        <p className="text-sm">No se pudo abrir el chat. Intentá de nuevo.</p>
      </div>
    )
  }

  return (
    <div className="flex h-[28rem] flex-col overflow-hidden rounded-2xl border border-on-surface/10 bg-surface">
      <div
        ref={scrollRef}
        className="flex-1 space-y-3 overflow-y-auto px-4 py-4"
        aria-live="polite"
      >
        {messagesLoading && messages.length === 0 ? (
          <div className="flex h-full items-center justify-center text-on-surface-variant">
            <Loader2 className="h-5 w-5 animate-spin" aria-hidden="true" />
          </div>
        ) : messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center gap-2 text-center text-on-surface-variant">
            <MessagesSquare className="h-7 w-7 opacity-50" aria-hidden="true" />
            <p className="text-sm">Todavía no hay mensajes. ¡Rompé el hielo!</p>
          </div>
        ) : (
          messages.map((message) =>
            message.kind === MessageKind.system ? (
              <SystemMessage key={message.id} message={message} />
            ) : (
              <MessageBubble key={message.id} message={message} currentUserId={currentUserId} />
            ),
          )
        )}
      </div>

      {isClosed && (
        <div className="border-t border-on-surface/10 bg-surface-container-high px-4 py-2.5 text-center text-xs text-on-surface-variant">
          Este chat cerró. El viaje finalizó hace 24 horas.
        </div>
      )}

      <MessageComposer threadId={thread.id} onMessageSent={refetch} disabled={isClosed} />
    </div>
  )
}
