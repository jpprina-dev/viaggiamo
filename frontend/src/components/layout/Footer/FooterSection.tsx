interface FooterSectionProps {
  title: string
  children: React.ReactNode
}

export function FooterSection({ title, children }: FooterSectionProps) {
  return (
    <div>
      <h3 className="font-semibold mb-4">{title}</h3>
      <ul className="space-y-2 text-gray-400 text-sm">
        {children}
      </ul>
    </div>
  )
}
