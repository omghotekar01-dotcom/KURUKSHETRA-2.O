type LoadingShimmerProps = {
  lines?: number
  compact?: boolean
  label?: string
}

export default function LoadingShimmer({ lines = 4, compact = false, label = 'Loading live evidence' }: LoadingShimmerProps) {
  return (
    <div className={`loading-shimmer ${compact ? 'compact' : ''}`} role="status" aria-live="polite" aria-label={label}>
      <div className="shimmer-heading" />
      {Array.from({ length: lines }).map((_, index) => (
        <div
          className="shimmer-line"
          style={{ width: `${Math.max(46, 94 - index * 11)}%` }}
          key={index}
        />
      ))}
      <span className="sr-only">{label}</span>
    </div>
  )
}
