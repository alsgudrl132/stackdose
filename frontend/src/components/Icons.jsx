// 직접 그린 작은 아이콘 몇 개 (글자 크기를 따라갑니다)
const base = {
  width: '1em',
  height: '1em',
  viewBox: '0 0 16 16',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 2,
  strokeLinecap: 'square',
  strokeLinejoin: 'miter',
  'aria-hidden': true,
  focusable: false,
}

export const PlusIcon = () => (
  <svg {...base}>
    <path d="M8 3v10M3 8h10" />
  </svg>
)

export const CloseIcon = () => (
  <svg {...base}>
    <path d="M4 4l8 8M12 4l-8 8" />
  </svg>
)

export const StopIcon = () => (
  <svg {...base}>
    <rect x="3.5" y="3.5" width="9" height="9" fill="currentColor" stroke="none" />
  </svg>
)

export const CheckIcon = () => (
  <svg {...base}>
    <path d="M3 8.5l3.2 3L13 4.5" />
  </svg>
)

export const AlertIcon = () => (
  <svg {...base}>
    <path d="M8 2.5l6 10.5H2z" strokeLinejoin="round" />
    <path d="M8 6.8v2.4M8 11.2v.1" />
  </svg>
)

export const ArrowIcon = () => (
  <svg {...base}>
    <path d="M2.5 8h10M8.5 4l4 4-4 4" />
  </svg>
)

// 로고: 쌓인 판 세 장 (stack)
export const Mark = () => (
  <svg width="24" height="24" viewBox="0 0 32 32" aria-hidden="true" focusable="false">
    <rect x="3" y="21" width="26" height="7" rx="1.5" fill="var(--accent)" />
    <rect x="6" y="12" width="20" height="6" rx="1.5" fill="currentColor" />
    <rect x="9" y="4" width="14" height="5" rx="1.5" fill="currentColor" opacity=".45" />
  </svg>
)
