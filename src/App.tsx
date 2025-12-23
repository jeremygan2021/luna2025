import { useState, useRef } from 'react';
import { SplashScreen } from './components/SplashScreen';
import { useLanguage } from './contexts/LanguageContext';
import { useSound } from './contexts/SoundContext';
import { MenuBar } from './components/MenuBar';
import { DesktopIcon } from './components/DesktopIcon';
import { FolderIcon, TrashIcon, DiskIcon, AppIcon, SnakeIcon, WeatherIcon, BluetoothIcon } from './components/Icons';
import { TodoApp } from './components/apps/TodoApp';
import { SnakeGame } from './components/apps/SnakeGame';
import { WeatherApp } from './components/apps/WeatherApp';
import { MacPaintApp } from './components/apps/MacPaintApp';
import { MacWriteApp } from './components/apps/MacWriteApp';
import { TrashApp } from './components/apps/TrashApp';
import { SuckesApp } from './components/apps/SuckesApp';
import { WifiConfigApp } from './components/apps/WifiConfigApp';
import { PlaceholderApp } from './components/apps/PlaceholderApp';

function App() {
  const { t } = useLanguage();
  const { playClick } = useSound();
  const [showSplash, setShowSplash] = useState(true);
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useRef<HTMLVideoElement>(null);

  // Desktop Icons state
  const [selectedIcon, setSelectedIcon] = useState<string | null>(null);
  
  // Window Management State
  const [activeApp, setActiveApp] = useState<string | null>('todo'); // Default to Todo app open

  const handleEnter = () => {
    playClick();
    setShowSplash(false);
    // Play music when entering app
    setTimeout(() => {
        if (audioRef.current) {
            audioRef.current.play().then(() => {
                setIsPlaying(true);
            }).catch(e => {
                console.log("Autoplay blocked or failed", e);
            });
        }
    }, 100);
  };

  const toggleMusic = () => {
    playClick();
    if (audioRef.current) {
        if (isPlaying) {
            audioRef.current.pause();
        } else {
            audioRef.current.play();
        }
        setIsPlaying(!isPlaying);
    }
  };

  const handleIconClick = (id: string) => {
    playClick();
    setSelectedIcon(id);
  }

  const handleIconDoubleClick = (id: string) => {
    playClick();
    setActiveApp(id);
  }

  const closeApp = () => {
    playClick();
    setActiveApp(null);
  }

  // Refactored Icon Lists
  // Mobile: Prioritize working apps and generic ones
  const mobileIcons = [
    { id: 'todo', label: t('todo'), icon: <AppIcon /> },
    { id: 'snake', label: t('snake'), icon: <SnakeIcon /> },
    { id: 'weather', label: t('weather'), icon: <WeatherIcon /> },
    { id: 'wifi', label: t('wifiConfig'), icon: <BluetoothIcon /> },
    { id: 'macpaint', label: t('macpaint'), icon: <AppIcon /> },
    { id: 'macwrite', label: t('macwrite'), icon: <AppIcon /> },
    { id: 'suckes', label: t('suckes'), icon: <FolderIcon /> },
    { id: 'trash', label: t('trash'), icon: <TrashIcon /> },
  ];

  const desktopIconsLeft = [
    { id: 'macpaint', label: t('macpaint'), icon: <AppIcon /> },
    { id: 'macwrite', label: t('macwrite'), icon: <AppIcon /> },
    { id: 'suckes', label: t('suckes'), icon: <FolderIcon /> },
    { id: 'diet', label: t('diet'), icon: <FolderIcon /> },
    { id: 'frash', label: t('frash'), icon: <FolderIcon /> },
    { id: 'ampow', label: t('ampow'), icon: <DiskIcon /> },
  ];

  const desktopIconsRight = [
    { id: 'hd', label: t('hd'), icon: <DiskIcon /> },
    { id: 'todo', label: t('todo'), icon: <AppIcon /> }, 
    { id: 'snake', label: t('snake'), icon: <SnakeIcon /> },
    { id: 'weather', label: t('weather'), icon: <WeatherIcon /> },
    { id: 'wifi', label: t('wifiConfig'), icon: <BluetoothIcon /> },
    { id: 'finder', label: t('finder'), icon: <FolderIcon /> },
    { id: 'trash', label: t('trash'), icon: <TrashIcon /> },
  ];

  const renderActiveApp = () => {
    if (!activeApp) return null;

    const commonProps = { onClose: closeApp };

    switch (activeApp) {
      case 'todo':
        return <TodoApp {...commonProps} isPlaying={isPlaying} toggleMusic={toggleMusic} />;
      case 'snake':
        return <SnakeGame {...commonProps} />;
      case 'weather':
        return <WeatherApp {...commonProps} />;
      case 'macpaint':
        return <MacPaintApp {...commonProps} />;
      case 'macwrite':
        return <MacWriteApp {...commonProps} />;
      case 'trash':
        return <TrashApp {...commonProps} />;
      case 'suckes':
        return <SuckesApp {...commonProps} />;
      case 'wifi':
        return <WifiConfigApp {...commonProps} />;
      default: {
        // Find label for title
        const allIcons = [...mobileIcons, ...desktopIconsLeft, ...desktopIconsRight];
        const icon = allIcons.find(i => i.id === activeApp);
        return <PlaceholderApp title={icon?.label || 'Application'} {...commonProps} />;
      }
    }
  };

  return (
    <>
      <video 
        ref={audioRef} 
        src="https://tangledup-ai-staging.oss-cn-shanghai.aliyuncs.com/Video/marry%20christmas%20lawrence.mp4" 
        loop 
        style={{ display: 'none' }} 
      />
      {showSplash ? (
        <SplashScreen onEnter={handleEnter} />
      ) : (
        <div style={{ 
          width: '100vw', 
          height: '100vh', 
          display: 'flex', 
          flexDirection: 'column', 
          overflow: 'hidden' 
        }}>
          <MenuBar onOpenApp={setActiveApp} />
          
          <div style={{ 
            flex: 1, 
            position: 'relative', 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center', 
            paddingTop: '28px' // Menu bar height
          }}>
            {/* Mobile Icons Grid - Visible only on mobile via CSS */}
            <div className="mobile-icons-grid" style={{
               display: 'none', // Controlled by CSS media query usually, but we'll enforce with class
            }}>
               {mobileIcons.map(icon => (
                <DesktopIcon 
                  key={icon.id}
                  icon={icon.icon}
                  label={icon.label}
                  selected={selectedIcon === icon.id}
                  onClick={() => {
                      handleIconClick(icon.id);
                      handleIconDoubleClick(icon.id);
                  }}
                />
              ))}
            </div>

            {/* Desktop Left Icons */}
            <div className="desktop-icons-left" style={{ 
              position: 'absolute', 
              left: '16px', 
              top: '16px', 
              display: 'flex', 
              flexDirection: 'column',
              zIndex: 1,
              maxHeight: 'calc(100vh - 60px)',
              flexWrap: 'wrap',
              alignContent: 'flex-start'
            }}>
              {desktopIconsLeft.map(icon => (
                <DesktopIcon 
                  key={icon.id}
                  icon={icon.icon}
                  label={icon.label}
                  selected={selectedIcon === icon.id}
                  onClick={() => handleIconClick(icon.id)}
                  // Double click handled via logic or just click for now
                />
              ))}
            </div>

            {/* Desktop Right Icons */}
            <div className="desktop-icons-right" style={{ 
              position: 'absolute', 
              right: '16px', 
              top: '16px', 
              display: 'flex', 
              flexDirection: 'column',
              zIndex: 1,
              maxHeight: 'calc(100vh - 60px)',
              flexWrap: 'wrap',
              alignContent: 'flex-start'
            }}>
              {desktopIconsRight.map(icon => (
                <DesktopIcon 
                  key={icon.id}
                  icon={icon.icon}
                  label={icon.label}
                  selected={selectedIcon === icon.id}
                  onClick={() => {
                      handleIconClick(icon.id);
                      handleIconDoubleClick(icon.id);
                  }}
                />
              ))}
            </div>

            {/* Central Window */}
            <div style={{ 
              zIndex: 10, 
              width: '100%', 
              maxWidth: '600px', 
              padding: '0 16px',
              animation: activeApp ? 'zoomIn 0.3s ease-out' : 'none',
              display: activeApp ? 'flex' : 'none',
              flexDirection: 'column',
              maxHeight: 'calc(100vh - 40px)' // Ensure it fits on screen
            }}>
              {renderActiveApp()}
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default App;
