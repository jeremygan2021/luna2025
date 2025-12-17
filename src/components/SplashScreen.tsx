import React, { useRef, useMemo } from 'react';
import { useLanguage } from '../contexts/LanguageContext';

interface SplashScreenProps {
  onEnter: () => void;
}

export const SplashScreen: React.FC<SplashScreenProps> = ({ onEnter }) => {
  const { t } = useLanguage();
  const videoRef = useRef<HTMLVideoElement>(null);

  const snowflakes = useMemo(() => Array.from({ length: 20 }).map((_, i) => ({
    id: i,
    left: Math.random() * 100,
    duration: Math.random() * 3 + 2,
    delay: Math.random() * 5
  })), []);

  const handleStart = () => {
    if (videoRef.current) {
      videoRef.current.play()
        .catch(err => console.error("Video play failed", err));
    }
    // We can also just enter immediately if user wants, but maybe let them watch a bit?
    // Let's make it so clicking "ENTER" enters the app.
    onEnter();
  };

  return (
    <div style={{ 
      position: 'fixed', 
      top: 0, 
      left: 0, 
      width: '100vw', 
      height: '100vh', 
      background: 'black', 
      color: 'white', 
      display: 'flex', 
      flexDirection: 'column', 
      alignItems: 'center', 
      justifyContent: 'center', 
      zIndex: 9999 
    }}>
      <video 
        ref={videoRef}
        src="/marry christmas lawrence.mp4" 
        style={{ width: '100%', maxWidth: '400px', marginBottom: '20px', border: '2px solid white' }}
        controls={false}
        loop
        autoPlay
        playsInline
        muted={false} // Autoplay might require muted, but user interaction allows unmuted.
      />
      
      <h1 style={{ fontFamily: 'var(--mac-font)', textAlign: 'center', marginBottom: '20px', whiteSpace: 'pre-line' }}>
        {t('splashTitle')}
      </h1>

      <button className="mac-btn" onClick={handleStart} style={{ fontSize: '18px', padding: '12px 24px' }}>
        {t('enterSystem')}
      </button>

      {/* Snow effect overlay */}
      {snowflakes.map((flake) => (
        <div 
          key={flake.id} 
          className="snowflake" 
          style={{ 
            left: `${flake.left}vw`, 
            animationDuration: `${flake.duration}s`, 
            animationDelay: `${flake.delay}s` 
          }} 
        />
      ))}
    </div>
  );
};
