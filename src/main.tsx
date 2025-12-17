import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { LanguageProvider } from './contexts/LanguageContext'
import { ModalProvider } from './contexts/ModalContext'
import { SoundProvider } from './contexts/SoundContext'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <LanguageProvider>
      <SoundProvider>
        <ModalProvider>
          <App />
        </ModalProvider>
      </SoundProvider>
    </LanguageProvider>
  </StrictMode>,
)
