import React from 'react';
import classNames from 'classnames';

interface MacWindowProps {
  title: string;
  children: React.ReactNode;
  className?: string;
  onClose?: () => void;
}

export const MacWindow: React.FC<MacWindowProps> = ({ title, children, className, onClose }) => {
  return (
    <div className={classNames('pixel-border bg-white flex flex-col', className)} style={{ background: 'var(--mac-white)', maxWidth: '100%', width: '600px', maxHeight: '90vh', display: 'flex', flexDirection: 'column' }}>
      <div className="title-bar" style={{ 
        background: 'var(--mac-black)', 
        color: 'var(--mac-white)', 
        padding: '4px 8px', 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        borderBottom: 'var(--mac-border)'
      }}>
        <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
           {onClose && <div onClick={onClose} style={{ width: '12px', height: '12px', background: 'var(--mac-white)', border: '1px solid black', cursor: 'pointer' }}></div>}
           <span style={{ fontWeight: 'bold', textTransform: 'uppercase', letterSpacing: '1px' }}>{title}</span>
        </div>
        <div style={{ display: 'flex', gap: '2px' }}>
          {/* Decorative lines */}
          <div style={{ width: '100%', height: '2px', background: 'var(--mac-white)' }}></div>
        </div>
      </div>
      <div className="content" style={{ padding: '16px', overflowY: 'auto', flex: 1 }}>
        {children}
      </div>
    </div>
  );
};
