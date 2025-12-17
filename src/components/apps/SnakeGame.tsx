import React, { useState, useEffect, useCallback, useRef } from 'react';
import { MacWindow } from '../MacWindow';
import { useSound } from '../../contexts/SoundContext';

// Game Constants
const GRID_SIZE = 20;
const CELL_SIZE = 15; // px
const INITIAL_SNAKE = [[10, 10], [10, 11], [10, 12]]; // Head at [10, 10]
const INITIAL_DIRECTION = [0, -1]; // Moving Up (row - 1)

interface SnakeGameProps {
  onClose: () => void;
}

export const SnakeGame: React.FC<SnakeGameProps> = ({ onClose }) => {
  const { playClick, playError } = useSound();
  const [snake, setSnake] = useState<number[][]>(INITIAL_SNAKE);
  const [food, setFood] = useState<number[]>([5, 5]);
  const [gameOver, setGameOver] = useState(false);
  const [score, setScore] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const gameLoopRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const directionRef = useRef(INITIAL_DIRECTION); // Ref to prevent multiple direction changes per tick

  const generateFood = useCallback(() => {
    let newFood: number[];
    do {
      newFood = [
        Math.floor(Math.random() * GRID_SIZE),
        Math.floor(Math.random() * GRID_SIZE)
      ];
    } while (snake.some(segment => segment[0] === newFood[0] && segment[1] === newFood[1]));
    return newFood;
  }, [snake]);

  const resetGame = () => {
    setSnake(INITIAL_SNAKE);
    directionRef.current = INITIAL_DIRECTION;
    setFood(generateFood());
    setGameOver(false);
    setScore(0);
    setIsPaused(false);
  };

  const moveSnake = useCallback(() => {
    if (gameOver || isPaused) return;

    setSnake(prevSnake => {
      const newHead = [
        prevSnake[0][0] + directionRef.current[0],
        prevSnake[0][1] + directionRef.current[1]
      ];

      // Check collisions
      if (
        newHead[0] < 0 || newHead[0] >= GRID_SIZE ||
        newHead[1] < 0 || newHead[1] >= GRID_SIZE ||
        prevSnake.some(segment => segment[0] === newHead[0] && segment[1] === newHead[1])
      ) {
        setGameOver(true);
        playError();
        return prevSnake;
      }

      const newSnake = [newHead, ...prevSnake];

      // Check food
      if (newHead[0] === food[0] && newHead[1] === food[1]) {
        setScore(prev => prev + 1);
        playClick(); // Satisfying sound on eat
        setFood(generateFood());
      } else {
        newSnake.pop(); // Remove tail
      }

      return newSnake;
    });
  }, [gameOver, isPaused, food, generateFood, playClick, playError]);

  useEffect(() => {
    gameLoopRef.current = setInterval(moveSnake, 150);
    return () => {
      if (gameLoopRef.current) clearInterval(gameLoopRef.current);
    };
  }, [moveSnake]);

  // Keyboard controls
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case 'ArrowUp':
          if (directionRef.current[1] !== 1) directionRef.current = [0, -1];
          break;
        case 'ArrowDown':
          if (directionRef.current[1] !== -1) directionRef.current = [0, 1];
          break;
        case 'ArrowLeft':
          if (directionRef.current[0] !== 1) directionRef.current = [-1, 0];
          break;
        case 'ArrowRight':
          if (directionRef.current[0] !== -1) directionRef.current = [1, 0];
          break;
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Mobile D-Pad Handlers
  const handleDirection = (dir: number[]) => {
    playClick();
    // Prevent reversing directly
    if (dir[0] !== -directionRef.current[0] || dir[1] !== -directionRef.current[1]) {
        directionRef.current = dir;
    }
  };

  return (
    <MacWindow title="Snake" onClose={onClose} className="snake-window">
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <div style={{ 
          marginBottom: '10px', 
          fontFamily: 'var(--mac-font)', 
          fontSize: '14px',
          display: 'flex',
          justifyContent: 'space-between',
          width: '100%'
        }}>
          <span>Score: {score}</span>
          <button className="mac-btn" onClick={resetGame} style={{ padding: '2px 8px', fontSize: '10px' }}>
            {gameOver ? 'RETRY' : 'RESET'}
          </button>
        </div>

        <div style={{
          width: GRID_SIZE * CELL_SIZE,
          height: GRID_SIZE * CELL_SIZE,
          border: '2px solid black',
          position: 'relative',
          background: 'white'
        }}>
          {gameOver && (
            <div style={{
              position: 'absolute',
              top: 0, left: 0, right: 0, bottom: 0,
              background: 'rgba(0,0,0,0.7)',
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 10
            }}>
              GAME OVER
            </div>
          )}
          
          {/* Food */}
          <div style={{
            position: 'absolute',
            left: food[0] * CELL_SIZE,
            top: food[1] * CELL_SIZE,
            width: CELL_SIZE - 2,
            height: CELL_SIZE - 2,
            background: 'black',
            borderRadius: '50%'
          }} />

          {/* Snake */}
          {snake.map((segment, i) => (
            <div key={i} style={{
              position: 'absolute',
              left: segment[0] * CELL_SIZE,
              top: segment[1] * CELL_SIZE,
              width: CELL_SIZE,
              height: CELL_SIZE,
              background: 'black',
              border: '1px solid white'
            }} />
          ))}
        </div>

        {/* Mobile Controls */}
        <div style={{ 
          marginTop: '20px', 
          display: 'grid', 
          gridTemplateColumns: '40px 40px 40px', 
          gap: '4px' 
        }}>
          <div />
          <button className="mac-btn" onClick={() => handleDirection([0, -1])}>▲</button>
          <div />
          <button className="mac-btn" onClick={() => handleDirection([-1, 0])}>◀</button>
          <button className="mac-btn" onClick={() => setIsPaused(!isPaused)}>{isPaused ? '▶' : 'II'}</button>
          <button className="mac-btn" onClick={() => handleDirection([1, 0])}>▶</button>
          <div />
          <button className="mac-btn" onClick={() => handleDirection([0, 1])}>▼</button>
          <div />
        </div>
      </div>
    </MacWindow>
  );
};
