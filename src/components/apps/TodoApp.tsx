import React, { useState, useEffect, useCallback } from 'react';
import { MacWindow } from '../MacWindow';
import { AddTodo } from '../AddTodo';
import { TodoList } from '../TodoList';
import { todoApi, type Todo } from '../../services/api';
import { useLanguage } from '../../contexts/LanguageContext';
import { useModal } from '../../contexts/ModalContext';
import { useSound } from '../../contexts/SoundContext';

interface TodoAppProps {
  onClose: () => void;
  isPlaying: boolean;
  toggleMusic: () => void;
}

export const TodoApp: React.FC<TodoAppProps> = ({ onClose, isPlaying, toggleMusic }) => {
  const { t, toggleLanguage } = useLanguage();
  const { showAlert, showConfirm } = useModal();
  const { playClick, playError } = useSound();
  const [todos, setTodos] = useState<Todo[]>([]);
  const [loading, setLoading] = useState(false);
  const [skip] = useState(0);
  const [limit] = useState(100);

  const fetchTodos = useCallback(async () => {
    setLoading(true);
    try {
      const data = await todoApi.getTodos(skip, limit);
      setTodos(data);
    } catch (error) {
      console.error('Failed to fetch todos', error);
    } finally {
      setLoading(false);
    }
  }, [skip, limit]);

  useEffect(() => {
    fetchTodos();
  }, [fetchTodos]);

  const handleAddTodo = async (title: string, description: string, dueDate: string) => {
    playClick();
    try {
      const newTodo = await todoApi.createTodo({
        title,
        description,
        due_date: dueDate ? new Date(dueDate).toISOString() : undefined,
        device_id: '1'
      });
      setTodos(prev => [newTodo, ...prev]);
    } catch (error) {
      playError();
      console.error('Failed to create todo', error);
      showAlert(t('createError'), 'Error');
    }
  };

  const handleToggleTodo = async (id: number, isCompleted: boolean) => {
    playClick();
    setTodos(prev => prev.map(t => t.id === id ? { ...t, is_completed: isCompleted } : t));
    
    try {
      if (isCompleted) {
        await todoApi.completeTodo(id);
      } else {
        await todoApi.incompleteTodo(id);
      }
      const updated = await todoApi.getTodo(id);
      setTodos(prev => prev.map(t => t.id === id ? updated : t));
    } catch (error) {
      playError();
      console.error('Failed to update todo', error);
      setTodos(prev => prev.map(t => t.id === id ? { ...t, is_completed: !isCompleted } : t));
    }
  };

  const handleDeleteTodo = async (id: number) => {
    playClick();
    const confirmed = await showConfirm(t('confirmDelete'), 'Confirm');
    if (!confirmed) return;
    
    const previousTodos = todos;
    setTodos(prev => prev.filter(t => t.id !== id));

    try {
      await todoApi.deleteTodo(id);
    } catch (error) {
      playError();
      console.error('Failed to delete todo', error);
      setTodos(previousTodos);
    }
  };

  return (
    <MacWindow title={t('windowTitle')} onClose={onClose}>
      <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '8px', gap: '8px' }}>
          <button className="mac-btn" onClick={toggleMusic} style={{ padding: '4px 8px', fontSize: '12px', minWidth: '60px' }}>
              {isPlaying ? '❚❚ MUSIC' : '▶ MUSIC'}
          </button>
          <button className="mac-btn" onClick={() => { playClick(); toggleLanguage(); }} style={{ padding: '4px 8px', fontSize: '12px' }}>
              {t('toggleLang').toUpperCase()}
          </button>
      </div>

      <AddTodo onAdd={handleAddTodo} />
      
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
        <span style={{ fontSize: '12px' }}>{todos.length} {t('items')}</span>
        <button className="mac-btn" onClick={() => { playClick(); fetchTodos(); }} style={{ padding: '4px 8px', fontSize: '12px' }}>
          {t('refresh').toUpperCase()}
        </button>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', minHeight: '0' }}>
          <TodoList 
          todos={todos} 
          onToggle={handleToggleTodo} 
          onDelete={handleDeleteTodo} 
          loading={loading}
          />
      </div>
      
      <div style={{ marginTop: '20px', textAlign: 'center', fontSize: '10px' }}>
        {t('footer')}
      </div>
    </MacWindow>
  );
};
