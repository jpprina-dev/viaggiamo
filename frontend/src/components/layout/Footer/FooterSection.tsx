interface FooterSectionProps {
  title: string
  children: React.ReactNode
}

export function FooterSection({ title, children }: FooterSectionProps) {
  return (
    <div>
      <h3 className="font-semibold mb-4 text-white/80 text-sm uppercase tracking-wider">{title}</h3>
      <ul className="space-y-3 text-sm">
        {children}
      </ul>
    </div>
  )
}
