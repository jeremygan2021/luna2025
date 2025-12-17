import React, { useRef, useState, useEffect } from 'react';
import { MacWindow } from '../MacWindow';
import { useLanguage } from '../../contexts/LanguageContext';

interface MacPaintAppProps {
  onClose: () => void;
}

export const MacPaintApp: React.FC<MacPaintAppProps> = ({ onClose }) => {
  const { t } = useLanguage();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [tool, setTool] = useState<'pencil' | 'eraser'>('pencil');

  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      }
    }
  }, []);

  const startDrawing = (e: React.MouseEvent | React.TouchEvent) => {
    setIsDrawing(true);
    draw(e);
  };

  const stopDrawing = () => {
    setIsDrawing(false);
    const canvas = canvasRef.current;
    if (canvas) {
        const ctx = canvas.getContext('2d');
        if (ctx) ctx.beginPath(); // Reset path
    }
  };

  const draw = (e: React.MouseEvent | React.TouchEvent) => {
    if (!isDrawing) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const rect = canvas.getBoundingClientRect();
    let x, y;

    if ('touches' in e) {
      x = e.touches[0].clientX - rect.left;
      y = e.touches[0].clientY - rect.top;
    } else {
      x = (e as React.MouseEvent).clientX - rect.left;
      y = (e as React.MouseEvent).clientY - rect.top;
    }

    ctx.lineWidth = tool === 'pencil' ? 2 : 10;
    ctx.lineCap = 'round';
    ctx.strokeStyle = tool === 'pencil' ? 'black' : 'white';

    ctx.lineTo(x, y);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(x, y);
  };

  const clearCanvas = () => {
    const canvas = canvasRef.current;
    if (canvas) {
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
      }
    }
  };

  return (
    <MacWindow title={t('macpaint')} onClose={onClose}>
      <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
        <div style={{ 
          display: 'flex', 
          gap: '8px', 
          padding: '8px', 
          borderBottom: '2px solid black',
          background: '#eee'
        }}>
          <button 
            className="mac-btn" 
            style={{ background: tool === 'pencil' ? 'black' : 'white', color: tool === 'pencil' ? 'white' : 'black' }}
            onClick={() => setTool('pencil')}
          >
            ✏️
          </button>
          <button 
            className="mac-btn" 
            style={{ background: tool === 'eraser' ? 'black' : 'white', color: tool === 'eraser' ? 'white' : 'black' }}
            onClick={() => setTool('eraser')}
          >
            🧽
          </button>
          <div style={{ flex: 1 }} />
          <button className="mac-btn" onClick={clearCanvas}>{t('clear')}</button>
        </div>
        <div style={{ flex: 1, overflow: 'hidden', background: '#888', padding: '10px' }}>
             <canvas
                ref={canvasRef}
                width={300}
                height={300}
                style={{ background: 'white', cursor: 'crosshair', width: '100%', height: '100%' }}
                onMouseDown={startDrawing}
                onMouseUp={stopDrawing}
                onMouseMove={draw}
                onMouseLeave={stopDrawing}
                onTouchStart={startDrawing}
                onTouchEnd={stopDrawing}
                onTouchMove={draw}
            />
        </div>
      </div>
    </MacWindow>
  );
};
