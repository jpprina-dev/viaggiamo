'use client'

import { format } from 'date-fns'
import type { Message } from '../types'

interface MessageBubbleProps {
  message: Message
  currentUserId: number
}

export function MessageBubble({ message, currentUserId }: MessageBubbleProps) {
  const isOwn = message.senderId === currentUserId
  const time = format(new Date(message.createdAt), 'HH:mm')

  return (
    <div className={`flex w-full ${isOwn ? 'justify-end' : 'justify-start'}`}>
      <div
        className={[
          'group max-w-[78%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed shadow-ambient transition-colors',
          isOwn
            ? 'rounded-br-md bg-primary-600 text-white'
            : 'rounded-bl-md bg-surface-container-high text-on-surface',
        ].join(' ')}
      >
        <p className="whitespace-pre-line break-words">{message.body}</p>
        <span
          className={[
            'mt-1 block text-right text-[10px] font-medium tabular-nums',
            isOwn ? 'text-white/70' : 'text-on-surface-variant',
          ].join(' ')}
        >
          {time}
        </span>
      </div>
    </div>
  )
}
