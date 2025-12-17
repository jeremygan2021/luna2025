import React from 'react';
import { MacWindow } from '../MacWindow';
import { useLanguage } from '../../contexts/LanguageContext';
import { TrashIcon } from '../Icons';

interface TrashAppProps {
  onClose: () => void;
}

export const TrashApp: React.FC<TrashAppProps> = ({ onClose }) => {
  const { t } = useLanguage();

  return (
    <MacWindow title={t('trash')} onClose={onClose}>
      <div style={{ 
          padding: '40px', 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center', 
          justifyContent: 'center',
          textAlign: 'center'
      }}>
        <div style={{ marginBottom: '20px' }}>
            <TrashIcon size={64} />
        </div>
        <p style={{ fontSize: '16px', marginBottom: '20px' }}>{t('trashEmpty')}</p>
        <button className="mac-btn" disabled style={{ opacity: 0.5 }}>{t('emptyTrash')}</button>
      </div>
    </MacWindow>
  );
};
