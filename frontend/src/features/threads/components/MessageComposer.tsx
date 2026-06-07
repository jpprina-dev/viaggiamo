'use client'

import { useState, useRef, useEffect, type FormEvent, type KeyboardEvent } from 'react'
import { Send } from 'lucide-react'
import { useSendMessage } from '../hooks/useSendMessage'

interface MessageComposerProps {
  threadId: number
  onMessageSent: () => void
  disabled?: boolean
}

const MAX_TEXTAREA_HEIGHT = 140

export function MessageComposer({ threadId, onMessageSent, disabled = false }: MessageComposerProps) {
  const [body, setBody] = useState('')
  const { sendMessage, loading, error, clearError } = useSendMessage()
  const textareaRef = useRef<HTMLTextAreaElement | null>(null)

  useEffect(() => {
    const el = textareaRef.current
    if (!el) return
    el.style.height = 'auto'
    el.style.height = `${Math.min(el.scrollHeight, MAX_TEXTAREA_HEIGHT)}px`
  }, [body])

  const trimmed = body.trim()
  const canSend = trimmed.length > 0 && !loading && !disabled

  const handleSubmit = async (event?: FormEvent) => {
    event?.preventDefault()
    if (!canSend) return
    try {
      await sendMessage(threadId, trimmed)
      setBody('')
      onMessageSent()
    } catch {
      // error surfaced via the hook's error state
    }
  }

  const handleKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      void handleSubmit()
    }
  }

  return (
    <form onSubmit={handleSubmit} className="border-t border-on-surface/10 bg-surface px-3 py-3">
      {error && (
        <p className="mb-2 px-1 text-xs font-medium text-error" role="alert">
          {error}
        </p>
      )}
      <div className="flex items-end gap-2">
        <textarea
          ref={textareaRef}
          value={body}
          onChange={(e) => {
            if (error) clearError()
            setBody(e.target.value)
          }}
          onKeyDown={handleKeyDown}
          disabled={disabled || loading}
          rows={1}
          placeholder={disabled ? 'El chat está cerrado' : 'Escribí un mensaje…'}
          aria-label="Mensaje"
          className="input-filled max-h-[140px] min-h-[44px] flex-1 resize-none rounded-2xl px-4 py-2.5 text-sm leading-relaxed disabled:opacity-60"
        />
        <button
          type="submit"
          disabled={!canSend}
          aria-label="Enviar mensaje"
          className="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-full bg-primary-600 text-white shadow-ambient transition-transform hover:scale-105 active:scale-95 disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:scale-100"
        >
          <Send className="h-4 w-4" aria-hidden="true" />
        </button>
      </div>
    </form>
  )
}
