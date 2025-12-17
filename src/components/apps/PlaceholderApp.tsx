import React from 'react';
import { MacWindow } from '../MacWindow';

interface PlaceholderAppProps {
  title: string;
  onClose: () => void;
}

export const PlaceholderApp: React.FC<PlaceholderAppProps> = ({ title, onClose }) => {
  return (
    <MacWindow title={title} onClose={onClose}>
      <div style={{ textAlign: 'center', padding: '40px 20px' }}>
        <div style={{ fontSize: '48px', marginBottom: '20px' }}>💣</div>
        <p style={{ marginBottom: '20px', lineHeight: '1.5' }}>
          The application "{title}" could not be opened because not enough memory is available.
        </p>
        <button className="mac-btn" onClick={onClose}>OK</button>
      </div>
    </MacWindow>
  );
};
