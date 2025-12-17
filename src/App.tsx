import { useState, useEffect, useCallback } from 'react';
import { SplashScreen } from './components/SplashScreen';
import { MacWindow } from './components/MacWindow';
import { AddTodo } from './components/AddTodo';
import { TodoList } from './components/TodoList';
import { todoApi, type Todo } from './services/api';
import { useLanguage } from './contexts/LanguageContext';

function App() {
  const { t, toggleLanguage } = useLanguage();
  const [showSplash, setShowSplash] = useState(true);
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
      // Optional: Show error in UI
    } finally {
      setLoading(false);
    }
  }, [skip, limit]);

  useEffect(() => {
    if (!showSplash) {
      fetchTodos();
    }
  }, [showSplash, fetchTodos]);

  const handleEnter = () => {
    setShowSplash(false);
  };

  const handleAddTodo = async (title: string, description: string) => {
    try {
      const newTodo = await todoApi.createTodo({
        title,
        description,
        device_id: '1' // Hardcoded as per requirement
      });
      // Prepend to list or re-fetch. Let's prepend.
      setTodos(prev => [newTodo, ...prev]);
    } catch (error) {
      console.error('Failed to create todo', error);
      alert(t('createError'));
    }
  };

  const handleToggleTodo = async (id: number, isCompleted: boolean) => {
    // Optimistic update
    setTodos(prev => prev.map(t => t.id === id ? { ...t, is_completed: isCompleted } : t));
    
    try {
      if (isCompleted) {
        await todoApi.completeTodo(id);
      } else {
        await todoApi.incompleteTodo(id);
      }
      // Ideally update with server response to get accurate timestamps
      const updated = await todoApi.getTodo(id);
      setTodos(prev => prev.map(t => t.id === id ? updated : t));
    } catch (error) {
      console.error('Failed to update todo', error);
      // Revert on failure
      setTodos(prev => prev.map(t => t.id === id ? { ...t, is_completed: !isCompleted } : t));
    }
  };

  const handleDeleteTodo = async (id: number) => {
    if (!window.confirm(t('confirmDelete'))) return;
    
    // Optimistic update
    const previousTodos = todos;
    setTodos(prev => prev.filter(t => t.id !== id));

    try {
      await todoApi.deleteTodo(id);
    } catch (error) {
      console.error('Failed to delete todo', error);
      setTodos(previousTodos);
    }
  };

  if (showSplash) {
    return <SplashScreen onEnter={handleEnter} />;
  }

  return (
    <div style={{ width: '100%', padding: '16px', display: 'flex', justifyContent: 'center' }}>
      <MacWindow title={t('windowTitle')}>
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '8px' }}>
            <button className="mac-btn" onClick={toggleLanguage} style={{ padding: '4px 8px', fontSize: '12px' }}>
                {t('toggleLang')}
            </button>
        </div>

        <AddTodo onAdd={handleAddTodo} />
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
          <span style={{ fontSize: '12px' }}>{todos.length} {t('items')}</span>
          <button className="mac-btn" onClick={fetchTodos} style={{ padding: '4px 8px', fontSize: '12px' }}>
            {t('refresh')}
          </button>
        </div>

        <TodoList 
          todos={todos} 
          onToggle={handleToggleTodo} 
          onDelete={handleDeleteTodo} 
          loading={loading}
        />
        
        <div style={{ marginTop: '20px', textAlign: 'center', fontSize: '10px' }}>
          {t('footer')}
        </div>
      </MacWindow>
    </div>
  );
}

export default App;
