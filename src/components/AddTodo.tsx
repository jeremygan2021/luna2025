import React, { useState } from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { useModal } from '../contexts/ModalContext';

interface AddTodoProps {
  onAdd: (title: string, description: string, dueDate: string) => void;
}

export const AddTodo: React.FC<AddTodoProps> = ({ onAdd }) => {
  const { t } = useLanguage();
  const { showAlert } = useModal();
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [dueDate, setDueDate] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    // Check for non-English characters (Printable ASCII only)
    const isEnglish = (text: string) => /^[ -~]*$/.test(text);

    if (!isEnglish(title) || !isEnglish(description)) {
      showAlert('Only English characters are allowed / 只能输入英文', 'Error');
      return;
    }

    onAdd(title, description, dueDate);
    setTitle('');
    setDescription('');
    setDueDate('');
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
          style={{ width: '100%', fontSize: '12px', marginBottom: '4px' }}
        />
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '12px' }}>Due:</span>
            <input 
            type="datetime-local" 
            className="mac-input" 
            value={dueDate}
            onChange={(e) => setDueDate(e.target.value)}
            style={{ flex: 1, fontSize: '12px' }}
            />
        </div>
      </div>
      <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
        <button type="submit" className="mac-btn">
          {t('addTask')}
        </button>
      </div>
    </form>
  );
};
