import React, { createContext, useContext, useState, useCallback } from 'react';
import { MacModal } from '../components/MacModal';

interface ModalContextType {
  showAlert: (message: string, title?: string) => Promise<void>;
  showConfirm: (message: string, title?: string) => Promise<boolean>;
}

const ModalContext = createContext<ModalContextType | undefined>(undefined);

export const ModalProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [modalState, setModalState] = useState<{
    isOpen: boolean;
    title?: string;
    message: string;
    type: 'alert' | 'confirm';
    resolve?: (value: any) => void;
  }>({
    isOpen: false,
    message: '',
    type: 'alert'
  });

  const showAlert = useCallback((message: string, title?: string) => {
    return new Promise<void>((resolve) => {
      setModalState({
        isOpen: true,
        title,
        message,
        type: 'alert',
        resolve: () => {
            resolve();
            setModalState(prev => ({ ...prev, isOpen: false }));
        }
      });
    });
  }, []);

  const showConfirm = useCallback((message: string, title?: string) => {
    return new Promise<boolean>((resolve) => {
      setModalState({
        isOpen: true,
        title,
        message,
        type: 'confirm',
        resolve: (confirmed: boolean) => {
            resolve(confirmed);
            setModalState(prev => ({ ...prev, isOpen: false }));
        }
      });
    });
  }, []);

  const handleConfirm = () => {
    if (modalState.resolve) {
      modalState.resolve(true); // For confirm: true; For alert: void (ignored)
    }
  };

  const handleCancel = () => {
    if (modalState.resolve) {
      modalState.resolve(false);
    }
  };

  return (
    <ModalContext.Provider value={{ showAlert, showConfirm }}>
      {children}
      <MacModal
        isOpen={modalState.isOpen}
        title={modalState.title}
        message={modalState.message}
        type={modalState.type}
        onConfirm={handleConfirm}
        onCancel={handleCancel}
      />
    </ModalContext.Provider>
  );
};

export const useModal = () => {
  const context = useContext(ModalContext);
  if (context === undefined) {
    throw new Error('useModal must be used within a ModalProvider');
  }
  return context;
};
