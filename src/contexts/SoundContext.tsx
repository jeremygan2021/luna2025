import React, { createContext, useContext, useCallback, useRef } from 'react';

interface SoundContextType {
  playClick: () => void;
  playError: () => void;
  playStartup: () => void;
}

const SoundContext = createContext<SoundContextType | undefined>(undefined);

export const SoundProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  // Using a short beep encoded as base64 to avoid external dependencies for simple sounds
  // This is a simple sine wave beep
  const clickSound = useRef<HTMLAudioElement | null>(null);

  const playClick = useCallback(() => {
    if (!clickSound.current) {
      // Create a simple oscillator beep using Web Audio API would be better, 
      // but for simplicity let's try a data URI or just the context approach.
      // Let's use Web Audio API for synthetic retro sounds.
      const AudioContext = window.AudioContext || (window as any).webkitAudioContext;
      if (AudioContext) {
        const ctx = new AudioContext();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'square'; // Square wave for 8-bit feel
        osc.frequency.setValueAtTime(800, ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(400, ctx.currentTime + 0.1);
        gain.gain.setValueAtTime(0.1, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.1);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.1);
      }
    }
  }, []);

  const playError = useCallback(() => {
      const AudioContext = window.AudioContext || (window as any).webkitAudioContext;
      if (AudioContext) {
        const ctx = new AudioContext();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(150, ctx.currentTime);
        gain.gain.setValueAtTime(0.2, ctx.currentTime);
        gain.gain.linearRampToValueAtTime(0, ctx.currentTime + 0.3);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.3);
      }
  }, []);

  const playStartup = useCallback(() => {
    // Startup chime is already handled by the video, but we could add a backup here
  }, []);

  return (
    <SoundContext.Provider value={{ playClick, playError, playStartup }}>
      {children}
    </SoundContext.Provider>
  );
};

export const useSound = () => {
  const context = useContext(SoundContext);
  if (context === undefined) {
    throw new Error('useSound must be used within a SoundProvider');
  }
  return context;
};
