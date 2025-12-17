import React from 'react';
import type { Todo } from '../services/api';

interface TodoItemProps {
  todo: Todo;
  onToggle: (id: number, isCompleted: boolean) => void;
  onDelete: (id: number) => void;
}

export const TodoItem: React.FC<TodoItemProps> = ({ todo, onToggle, onDelete }) => {
  return (
    <div style={{ 
      borderBottom: '1px dashed black', 
      padding: '8px 0', 
      display: 'flex', 
      alignItems: 'flex-start',
      gap: '8px',
      opacity: todo.is_completed ? 0.6 : 1
    }}>
      <input 
        type="checkbox" 
        checked={todo.is_completed} 
        onChange={() => onToggle(todo.id, !todo.is_completed)}
        style={{ marginTop: '4px', cursor: 'pointer' }}
      />
      <div style={{ flex: 1 }}>
        <div style={{ 
          fontWeight: 'bold', 
          textDecoration: todo.is_completed ? 'line-through' : 'none' 
        }}>
          {todo.title}
        </div>
        {todo.description && (
          <div style={{ fontSize: '12px', marginTop: '4px' }}>
            {todo.description}
          </div>
        )}
        {todo.due_date && (
            <div style={{ fontSize: '10px', marginTop: '2px', color: '#666' }}>
                Due: {new Date(todo.due_date).toLocaleString()}
            </div>
        )}
      </div>
      <button 
        onClick={() => onDelete(todo.id)}
        style={{ 
          background: 'none', 
          border: 'none', 
          cursor: 'pointer', 
          fontFamily: 'var(--mac-font)',
          fontWeight: 'bold'
        }}
      >
        [X]
      </button>
    </div>
  );
};
