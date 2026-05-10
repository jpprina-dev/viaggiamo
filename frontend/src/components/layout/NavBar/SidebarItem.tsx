import Link from 'next/link'
import type { LucideIcon } from 'lucide-react'
import { cn } from '@/utils/cn'

interface SidebarItemProps {
  icon: LucideIcon
  label: string
  href: string
  isActive: boolean
  expanded: boolean
  isDisabled?: boolean
  badge?: string
}

export function SidebarItem({
  icon: Icon,
  label,
  href,
  isActive,
  expanded,
  isDisabled = false,
  badge,
}: SidebarItemProps) {
  const inner = (
    <span
      className={cn(
        'flex items-center w-full px-3 py-2 rounded-xl transition-colors duration-200',
        isActive && 'bg-primary-container text-[#00210b]',
        !isActive && !isDisabled && 'text-white/70 hover:text-white hover:bg-white/10',
        isDisabled && 'text-white/30 cursor-not-allowed opacity-50',
      )}
    >
      <Icon className="w-5 h-5 flex-shrink-0" aria-hidden="true" />
      <span
        className={cn(
          'ml-3 text-sm font-medium whitespace-nowrap overflow-hidden transition-all duration-300',
          expanded ? 'opacity-100 max-w-[140px]' : 'opacity-0 max-w-0',
        )}
      >
        {label}
      </span>
      {badge && expanded && (
        <span className="ml-auto text-[10px] bg-white/10 text-white/50 px-1.5 py-0.5 rounded-full leading-tight">
          {badge}
        </span>
      )}
    </span>
  )

  if (isDisabled) {
    return (
      <div role="presentation" aria-label={label} aria-disabled="true">
        {inner}
      </div>
    )
  }

  return <Link href={href}>{inner}</Link>
}
