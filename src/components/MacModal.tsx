import React from 'react';
import { MacWindow } from './MacWindow';

interface MacModalProps {
  isOpen: boolean;
  title?: string;
  message: string;
  type: 'alert' | 'confirm';
  onConfirm: () => void;
  onCancel: () => void;
}

export const MacModal: React.FC<MacModalProps> = ({ 
  isOpen, 
  title = 'System', 
  message, 
  type, 
  onConfirm, 
  onCancel 
}) => {
  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      width: '100vw',
      height: '100vh',
      background: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      zIndex: 9999
    }}>
      <div style={{ width: '400px', maxWidth: '90%' }}>
        <MacWindow title={title} onClose={type === 'confirm' ? onCancel : onConfirm}>
          <div style={{ padding: '20px 0', textAlign: 'center', fontSize: '16px', lineHeight: '1.5' }}>
            {message}
          </div>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '16px', marginTop: '16px' }}>
            {type === 'confirm' && (
              <button className="mac-btn" onClick={onCancel}>
                Cancel
              </button>
            )}
            <button className="mac-btn" onClick={onConfirm}>
              OK
            </button>
          </div>
        </MacWindow>
      </div>
    </div>
  );
};
