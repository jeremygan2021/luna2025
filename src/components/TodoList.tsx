import React from 'react';
import type { Todo } from '../services/api';
import { TodoItem } from './TodoItem';
import { useLanguage } from '../contexts/LanguageContext';

interface TodoListProps {
  todos: Todo[];
  onToggle: (id: number, isCompleted: boolean) => void;
  onDelete: (id: number) => void;
  loading: boolean;
}

export const TodoList: React.FC<TodoListProps> = ({ todos, onToggle, onDelete, loading }) => {
  const { t } = useLanguage();

  if (loading && todos.length === 0) {
    return <div style={{ textAlign: 'center', padding: '20px' }}>{t('loading')}</div>;
  }

  if (todos.length === 0) {
    return <div style={{ textAlign: 'center', padding: '20px' }}>{t('noTasks')}</div>;
  }

  return (
    <div>
      {todos.map(todo => (
        <TodoItem 
          key={todo.id} 
          todo={todo} 
          onToggle={onToggle} 
          onDelete={onDelete} 
        />
      ))}
    </div>
  );
};
