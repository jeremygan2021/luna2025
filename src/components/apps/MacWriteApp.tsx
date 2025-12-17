import React, { useState } from 'react';
import { MacWindow } from '../MacWindow';
import { useLanguage } from '../../contexts/LanguageContext';

interface MacWriteAppProps {
  onClose: () => void;
}

export const MacWriteApp: React.FC<MacWriteAppProps> = ({ onClose }) => {
  const { t } = useLanguage();
  const [text, setText] = useState('Welcome to MacWrite!\n\nThis is a simple text editor.');

  return (
    <MacWindow title={t('macwrite')} onClose={onClose}>
      <div style={{ display: 'flex', flexDirection: 'column', height: '300px' }}>
        <div style={{ 
          display: 'flex', 
          gap: '8px', 
          padding: '4px', 
          borderBottom: '1px solid black',
          fontSize: '12px'
        }}>
           <span>{t('file')}</span>
           <span>{t('edit')}</span>
           <span>Format</span>
           <span>Font</span>
           <span>Style</span>
        </div>
        <div style={{ 
            background: 'white', 
            padding: '2px', 
            borderBottom: '1px solid black', 
            marginBottom: '4px' 
        }}>
            {/* Ruler simulation */}
            <div style={{ 
                height: '15px', 
                backgroundImage: 'linear-gradient(to right, black 1px, transparent 1px)',
                backgroundSize: '10px 100%',
                borderBottom: '1px solid black'
            }} />
        </div>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          style={{
            flex: 1,
            width: '100%',
            border: 'none',
            resize: 'none',
            fontFamily: 'Courier New, monospace',
            fontSize: '14px',
            padding: '8px',
            outline: 'none',
            lineHeight: '1.5'
          }}
        />
      </div>
    </MacWindow>
  );
};
