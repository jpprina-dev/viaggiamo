interface GradientIconProps {
  width?: number
  height?: number
  className?: string
}

export function GradientIcon({ width = 32, height = 32, className = '' }: GradientIconProps) {
  // Unique gradient ID to avoid conflicts with icon0.svg
  const gradientId = `viajamos-gradient-${Math.random().toString(36).substr(2, 9)}`

  return (
    <svg
      width={width}
      height={height}
      viewBox="0 0 242.37305 291.41867"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <defs>
        <linearGradient id={gradientId} x1="0%" y1="50%" x2="100%" y2="50%">
          <stop offset="0%" style={{ stopColor: '#48A79F', stopOpacity: 1 }} />
          <stop offset="100%" style={{ stopColor: '#7CE495', stopOpacity: 1 }} />
        </linearGradient>
      </defs>
      <g transform="translate(-11484.57,-463.68802)">
        <path
          d="m 929.237,725.216 c -2.512,-8.885 -3.846,-18.273 -3.846,-27.975 v 0 c 0,-9.2 1.208,-18.117 3.469,-26.611 v 0 c 7.488,-28.133 26.594,-51.525 51.855,-64.774 v 0 c -15.888,16.845 -25.621,39.562 -25.621,64.523 v 0 c 0,5.526 0.47,10.943 1.396,16.201 v 0 c 2.261,0.362 4.585,0.55 6.939,0.55 v 0 c 24.569,0 44.477,-19.906 44.477,-44.475 v 0 c 0,-16.736 -20.118,-38.524 -21.132,-39.719 v 0 l -18.148,-18.148 -5.322,-5.338 -18.173,16.157 c -11.672,10.905 -18.469,17.109 -25.753,27.769 v 0 c -11.288,16.531 -17.881,36.517 -17.881,58.055 v 0 c 0,10.221 1.491,20.111 4.254,29.421 v 0 c -13.721,-11.571 -23.972,-27.145 -28.949,-44.9 v 0 c -2.198,-7.834 -3.375,-16.076 -3.375,-24.616 v 0 c 0,-23.329 6.242,-40.382 23.25,-60.693 v 0 L 963.65,513.67 c 0,0 54.936,50.836 74,77.968 v 0 c 9.045,12.871 17.557,32.822 17.557,49.698 v 0 c 0,9.106 -1.335,17.912 -3.831,26.201 v 0 c -10.032,33.361 -38.683,58.637 -73.896,63.739 v 0 c -4.301,0.628 -8.698,0.958 -13.171,0.958 v 0 c -12.434,0 -24.287,-2.496 -35.072,-7.018"
          fill={`url(#${gradientId})`}
          style={{ stroke: 'none' }}
          transform="matrix(1.3333333,0,0,-1.3333333,10320,1440)"
        />
      </g>
    </svg>
  )
}
