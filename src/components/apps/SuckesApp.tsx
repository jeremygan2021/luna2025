import React from 'react';
import { MacWindow } from '../MacWindow';
import { useLanguage } from '../../contexts/LanguageContext';
import { FolderIcon } from '../Icons';

interface SuckesAppProps {
  onClose: () => void;
}

export const SuckesApp: React.FC<SuckesAppProps> = ({ onClose }) => {
  const { t } = useLanguage();

  const files = [
    { name: 'System', size: '24K' },
    { name: 'Finder', size: '42K' },
    { name: 'Note Pad', size: '4K' },
    { name: 'Scrapbook', size: '12K' },
    { name: 'Clipboard', size: '8K' },
  ];

  return (
    <MacWindow title={t('suckes')} onClose={onClose}>
      <div style={{ padding: '8px' }}>
        <div style={{ 
            display: 'flex', 
            borderBottom: '1px solid black', 
            paddingBottom: '4px',
            marginBottom: '4px',
            fontWeight: 'bold',
            fontSize: '12px'
        }}>
            <span style={{ flex: 2 }}>Name</span>
            <span style={{ flex: 1 }}>Size</span>
            <span style={{ flex: 1 }}>Kind</span>
        </div>
        {files.map((file, i) => (
            <div key={i} style={{ 
                display: 'flex', 
                padding: '4px 0',
                cursor: 'pointer',
                fontSize: '12px'
            }} className="file-row">
                <span style={{ flex: 2, display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <FolderIcon size={12} /> {file.name}
                </span>
                <span style={{ flex: 1 }}>{file.size}</span>
                <span style={{ flex: 1 }}>Application</span>
            </div>
        ))}
        <div style={{ marginTop: '20px', borderTop: '1px dotted black', paddingTop: '8px', fontSize: '12px' }}>
            5 items, 340K in disk, 60K available
        </div>
      </div>
    </MacWindow>
  );
};
