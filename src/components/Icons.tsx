export const AppleIcon = ({ size = 24 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
    <path d="M17.2,14.6c-0.2,2-1.8,4.6-3.3,4.6c-0.8,0-1.4-0.6-2.5-0.6c-1.1,0-1.6,0.6-2.5,0.6c-1.5,0-3.4-2.8-3.4-5.1c0-2.8,1.7-4.2,3.3-4.2c0.9,0,1.5,0.6,2.1,0.6c0.6,0,1.6-0.7,2.8-0.7C15.5,9.8,16.8,10.6,17.2,11.5c-1.5,0.8-1.2,3-0.1,3.5L17.2,14.6z M13.8,7.3c-0.7-0.9-0.6-2.1-0.5-2.6C14.2,4.8,15.2,5.7,15.6,6.4C16.3,7.2,16.2,8.6,16.1,8.9C15.2,8.9,14.4,8.1,13.8,7.3z"/>
  </svg>
);

export const FolderIcon = ({ size = 32 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 32 32" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M2 6h8l2 2h18v20H2V6z" />
    <path d="M2 10h28" strokeWidth="1"/>
  </svg>
);

export const TrashIcon = ({ size = 32 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 32 32" fill="none" stroke="currentColor" strokeWidth="2">
    <path d="M6 6h20v24H6z" />
    <path d="M10 6V2h12v4" />
    <path d="M8 10v16M12 10v16M16 10v16M20 10v16M24 10v16" strokeWidth="1" />
  </svg>
);

export const DiskIcon = ({ size = 32 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 32 32" fill="none" stroke="currentColor" strokeWidth="2">
    <rect x="4" y="4" width="24" height="24" rx="2" />
    <rect x="8" y="4" width="16" height="12" fill="white" stroke="currentColor" />
    <rect x="10" y="22" width="12" height="6" fill="white" stroke="currentColor" />
  </svg>
);

export const AppIcon = ({ size = 32 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 32 32" fill="none" stroke="currentColor" strokeWidth="2">
    <rect x="4" y="4" width="24" height="24" />
    <path d="M4 10h24M10 4v24M22 4v24" strokeWidth="1" />
    <circle cx="16" cy="19" r="4" fill="currentColor" />
  </svg>
);

export const SnakeIcon = ({ size = 32 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 32 32" fill="none" stroke="currentColor" strokeWidth="2">
    <rect x="4" y="4" width="24" height="24" />
    <path d="M8 24c0-4 4-4 4-8s-4-4-4-8 8 0 8 4 4 4 4 8" strokeWidth="2" strokeLinecap="round" />
    <circle cx="20" cy="24" r="2" fill="currentColor" />
  </svg>
);

export const WeatherIcon = ({ size = 32 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 32 32" fill="none" stroke="currentColor" strokeWidth="2">
    <circle cx="16" cy="16" r="8" />
    <path d="M16 4v4M16 24v4M4 16h4M24 16h4M7.5 7.5l2.8 2.8M21.7 21.7l2.8 2.8M7.5 24.5l2.8-2.8M21.7 10.3l2.8-2.8" strokeWidth="2" />
  </svg>
);
