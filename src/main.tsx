import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { LanguageProvider } from './contexts/LanguageContext.tsx'
import { ModalProvider } from './contexts/ModalContext.tsx'
import { SoundProvider } from './contexts/SoundContext.tsx'

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
