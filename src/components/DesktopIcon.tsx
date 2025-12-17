import React from 'react';

interface DesktopIconProps {
  icon: React.ReactNode;
  label: string;
  onClick?: () => void;
  selected?: boolean;
}

export const DesktopIcon: React.FC<DesktopIconProps> = ({ icon, label, onClick, selected }) => {
  return (
    <div 
      onClick={onClick}
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        width: '80px',
        cursor: 'pointer',
        padding: '4px',
        marginBottom: '16px'
      }}
    >
      <div style={{ 
        marginBottom: '4px',
        background: selected ? 'black' : 'transparent',
        color: selected ? 'white' : 'black',
        padding: '2px'
      }}>
        {icon}
      </div>
      <span style={{ 
        background: selected ? 'black' : 'white',
        color: selected ? 'white' : 'black',
        padding: '2px 4px',
        fontSize: '12px',
        textAlign: 'center',
        border: '1px solid black',
        maxWidth: '100%',
        wordWrap: 'break-word'
      }}>
        {label}
      </span>
    </div>
  );
};
