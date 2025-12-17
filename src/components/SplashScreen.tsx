import React, { useRef, useState, useEffect } from 'react';
import { useLanguage } from '../contexts/LanguageContext';
import { AppleIcon } from './Icons';

interface SplashScreenProps {
  onEnter: () => void;
}

export const SplashScreen: React.FC<SplashScreenProps> = ({ onEnter }) => {
  const { t } = useLanguage();
  const videoRef = useRef<HTMLVideoElement>(null);
  const [progress, setProgress] = useState(0);

  // Auto-progress bar
  useEffect(() => {
    const timer = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(timer);
          return 100;
        }
        return prev + 2;
      });
    }, 50);
    return () => clearInterval(timer);
  }, []);

  const [snowflakes] = useState(() => Array.from({ length: 20 }).map((_, i) => ({
    id: i,
    left: Math.random() * 100,
    duration: Math.random() * 3 + 2,
    delay: Math.random() * 5
  })));

  const handleStart = () => {
    if (videoRef.current) {
      videoRef.current.play()
        .catch(err => console.error("Video play failed", err));
    }
    onEnter();
  };

  return (
    <div style={{ 
      position: 'fixed', 
      top: 0, 
      left: 0, 
      width: '100vw', 
      height: '100vh', 
      background: 'white', 
      color: 'black', 
      display: 'flex', 
      flexDirection: 'column', 
      alignItems: 'center', 
      justifyContent: 'center', 
      zIndex: 9999,
      fontFamily: 'var(--mac-font)'
    }}>
      {/* Hidden Video for Audio */}
      <video 
        ref={videoRef}
        src="https://tangledup-ai-staging.oss-cn-shanghai.aliyuncs.com/Video/marry%20christmas%20lawrence.mp4" 
        style={{ display: 'none' }}
        controls={false}
        loop
        autoPlay
        playsInline
        muted={false} 
      />
      
      {/* Retro Apple Logo with Santa Hat (CSS/SVG) */}
      <div style={{ position: 'relative', marginBottom: '40px', transform: 'scale(4)' }}>
        <div style={{ position: 'absolute', top: -12, left: -5, zIndex: 10, transform: 'rotate(-15deg)' }}>
             {/* Simple SVG Santa Hat */}
            <svg width="40" height="30" viewBox="0 0 40 30" fill="none">
                <path d="M5 25 Q 20 0 35 25" fill="white" stroke="black" strokeWidth="2"/>
                <circle cx="35" cy="25" r="4" fill="white" stroke="black" strokeWidth="2"/>
                <rect x="5" y="23" width="30" height="6" rx="3" fill="white" stroke="black" strokeWidth="2"/>
            </svg>
        </div>
        <AppleIcon size={64} />
        {/* Christmas Lights placeholder - simplified as dots */}
        <div style={{ position: 'absolute', width: '100%', height: '100%', top: 0, left: 0, pointerEvents: 'none' }}>
            <div style={{ position: 'absolute', top: '50%', left: '10%', width: '4px', height: '4px', background: 'black', borderRadius: '50%' }}></div>
            <div style={{ position: 'absolute', top: '60%', left: '80%', width: '4px', height: '4px', background: 'black', borderRadius: '50%' }}></div>
            <div style={{ position: 'absolute', top: '30%', left: '60%', width: '4px', height: '4px', background: 'black', borderRadius: '50%' }}></div>
        </div>
      </div>

      <h1 style={{ 
        fontFamily: 'var(--mac-font)', 
        textAlign: 'center', 
        marginBottom: '20px', 
        fontSize: '24px',
        fontWeight: 'bold'
      }}>
        Welcome to MacnOiosch
      </h1>

      {/* Retro Progress Bar */}
      <div style={{ 
        width: '300px', 
        height: '24px', 
        border: '2px solid black', 
        padding: '2px',
        marginBottom: '20px',
        position: 'relative'
      }}>
        <div style={{ 
          width: `${progress}%`, 
          height: '100%', 
          background: `repeating-linear-gradient(
            45deg,
            black,
            black 10px,
            white 10px,
            white 20px
          )`,
          transition: 'width 0.1s linear'
        }} />
      </div>

      <div style={{ marginBottom: '40px', fontSize: '18px' }}>
        Merry Christmas Miss Luna
      </div>

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
            animationDelay: `${flake.delay}s`,
            background: 'black' // Black snow for retro look
          }} 
        />
      ))}

      <div style={{
        position: 'absolute',
        bottom: '20px',
        fontSize: '12px',
        fontFamily: 'var(--mac-font)'
      }}>
        <a 
          href="https://beian.miit.gov.cn/" 
          target="_blank" 
          rel="noopener noreferrer"
          style={{ color: 'black', textDecoration: 'none' }}
        >
          滇ICP备2023013157号-3
        </a>
      </div>
    </div>
  );
};
