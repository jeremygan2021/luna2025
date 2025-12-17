import React, { useState } from 'react';
import { useLanguage } from '../contexts/LanguageContext';

interface AddTodoProps {
  onAdd: (title: string, description: string) => void;
}

export const AddTodo: React.FC<AddTodoProps> = ({ onAdd }) => {
  const { t } = useLanguage();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;
    onAdd(title, description);
    setTitle('');
    setDescription('');
  };

  return (
    <form onSubmit={handleSubmit} style={{ 
      border: 'var(--mac-border)', 
      padding: '8px', 
      marginBottom: '16px',
      background: '#eee'
    }}>
      <div style={{ marginBottom: '8px' }}>
        <input 
          type="text" 
          className="mac-input" 
          placeholder={t('newTaskPlaceholder')}
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          style={{ width: '100%', marginBottom: '4px' }}
        />
        <input 
          type="text" 
          className="mac-input" 
          placeholder={t('descriptionPlaceholder')}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          style={{ width: '100%', fontSize: '12px' }}
        />
      </div>
      <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
        <button type="submit" className="mac-btn">
          {t('addTask')}
        </button>
      </div>
    </form>
  );
};
