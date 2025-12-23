import React, { useState, useEffect } from 'react';
import { MacWindow } from '../MacWindow';
import { useLanguage } from '../../contexts/LanguageContext';

interface WifiConfigAppProps {
  onClose: () => void;
}

// Minimal Web Bluetooth Type Definitions
interface BluetoothDevice extends EventTarget {
  id: string;
  name?: string;
  gatt?: BluetoothRemoteGATTServer;
}

interface BluetoothRemoteGATTServer {
  device: BluetoothDevice;
  connected: boolean;
  connect(): Promise<BluetoothRemoteGATTServer>;
  disconnect(): void;
  getPrimaryService(service: string): Promise<BluetoothRemoteGATTService>;
}

interface BluetoothRemoteGATTService {
  getCharacteristic(characteristic: string): Promise<BluetoothRemoteGATTCharacteristic>;
}

interface BluetoothRemoteGATTCharacteristic extends EventTarget {
  value: DataView;
  startNotifications(): Promise<BluetoothRemoteGATTCharacteristic>;
  writeValue(value: BufferSource): Promise<void>;
}

// Extend Navigator interface
declare global {
  interface Navigator {
    bluetooth: {
      requestDevice(options: { filters: any[], optionalServices?: string[] }): Promise<BluetoothDevice>;
    };
  }
}

const NUS_SERVICE_UUID = "6e400001-b5a3-f393-e0a9-e50e24dcca9e";
const NUS_RX_CHARACTERISTIC_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e";
const NUS_TX_CHARACTERISTIC_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e";

export const WifiConfigApp: React.FC<WifiConfigAppProps> = ({ onClose }) => {
  const { t, toggleLanguage } = useLanguage();
  const [device, setDevice] = useState<BluetoothDevice | null>(null);
  const [, setServer] = useState<BluetoothRemoteGATTServer | null>(null);
  const [rxChar, setRxChar] = useState<BluetoothRemoteGATTCharacteristic | null>(null);
  const [status, setStatus] = useState<string>("readyToConnect");
  const [ssid, setSsid] = useState("");
  const [password, setPassword] = useState("");
  const [logs, setLogs] = useState<string[]>([]);
  const [isScanning, setIsScanning] = useState(false);

  const addLog = (msg: string) => {
    setLogs(prev => [...prev, `> ${msg}`].slice(-10));
    // Check if msg is a translation key, if not, use it as is (for dynamic logs)
    // But for status we want to use keys mostly.
    // For now, let's just set status to msg and handle translation in render if possible, 
    // or just pass translated string here.
    // To simplify, we'll keep log history as is, but status we might want to be careful.
    // Actually, status update is tricky with translation. 
    // Let's assume for now we pass translation keys where applicable, or raw strings.
    setStatus(msg);
  };

  const connectToDevice = async () => {
    try {
      setIsScanning(true);
      addLog(t('requestingDevice'));
      
      const device = await navigator.bluetooth.requestDevice({
        filters: [{ namePrefix: 'Luna' }], 
        optionalServices: [NUS_SERVICE_UUID]
      });

      setDevice(device);
      addLog(`${t('connectingTo')} ${device.name}...`);
      
      device.addEventListener('gattserverdisconnected', onDisconnected);

      const server = await device.gatt?.connect();
      if (!server) throw new Error("Could not connect to GATT Server");
      setServer(server);

      addLog(t('gettingService'));
      const service = await server.getPrimaryService(NUS_SERVICE_UUID);

      addLog(t('gettingCharacteristics'));
      const rx = await service.getCharacteristic(NUS_RX_CHARACTERISTIC_UUID);
      const tx = await service.getCharacteristic(NUS_TX_CHARACTERISTIC_UUID);

      setRxChar(rx);

      await tx.startNotifications();
      tx.addEventListener('characteristicvaluechanged', handleNotifications);
      
      addLog(t('connected'));
      setIsScanning(false);

    } catch (error) {
      console.error(error);
      addLog(`${t('error')}: ${(error as Error).message}`);
      setIsScanning(false);
    }
  };

  const onDisconnected = () => {
    addLog(t('disconnected'));
    setDevice(null);
    setServer(null);
    setRxChar(null);
  };

  const handleNotifications = (event: Event) => {
    const value = (event.target as BluetoothRemoteGATTCharacteristic).value;
    const decoder = new TextDecoder('utf-8');
    const str = decoder.decode(value);
    addLog(`${t('received')}: ${str}`);
  };

  const sendConfig = async () => {
    if (!rxChar) {
      addLog(t('notConnected'));
      return;
    }

    if (!ssid || !password) {
      addLog(t('pleaseEnterCredentials'));
      return;
    }

    const payload = {
      ssid: ssid,
      password: password
    };

    try {
      const encoder = new TextEncoder();
      const data = encoder.encode(JSON.stringify(payload));
      await rxChar.writeValue(data);
      addLog(t('wifiConfigSent'));
    } catch (error) {
      addLog(`${t('sendFailed')}: ${(error as Error).message}`);
    }
  };

  const disconnect = () => {
    if (device && device.gatt?.connected) {
      device.gatt.disconnect();
    }
  };

  useEffect(() => {
    return () => {
      if (device && device.gatt?.connected) {
        device.gatt.disconnect();
      }
    };
  }, [device]);

  return (
    <MacWindow title={t('wifiConfig')} onClose={onClose}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        
        {/* Language Toggle */}
        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
            <button 
                onClick={toggleLanguage}
                style={{
                    background: 'transparent',
                    border: '1px solid black',
                    padding: '4px 8px',
                    cursor: 'pointer',
                    fontFamily: 'inherit',
                    fontSize: '12px'
                }}
            >
                {t('toggleLang')}
            </button>
        </div>

        <div style={{ padding: '16px', border: '2px solid black', background: '#f0f0f0' }}>
          <p style={{ margin: '0 0 10px 0', fontWeight: 'bold' }}>{t('status')}: {status}</p>
          
          {!device ? (
            <button 
              className="mac-btn" 
              onClick={connectToDevice}
              disabled={isScanning}
              style={{
                background: 'white',
                border: '2px solid black',
                padding: '8px 16px',
                fontFamily: 'inherit',
                cursor: 'pointer',
                boxShadow: '2px 2px 0px 0px black'
              }}
            >
              {isScanning ? t('scanning') : t('connectToLuna')}
            </button>
          ) : (
            <button 
              className="mac-btn" 
              onClick={disconnect}
              style={{
                background: 'white',
                border: '2px solid black',
                padding: '8px 16px',
                fontFamily: 'inherit',
                cursor: 'pointer',
                boxShadow: '2px 2px 0px 0px black'
              }}
            >
              {t('disconnect')}
            </button>
          )}
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '4px', fontWeight: 'bold' }}>{t('wifiSsid')}:</label>
            <input 
              type="text" 
              value={ssid} 
              onChange={(e) => setSsid(e.target.value)}
              style={{ 
                width: '100%', 
                padding: '8px', 
                border: '2px solid black',
                fontFamily: 'inherit',
                fontSize: '16px'
              }}
              placeholder={t('enterSsid')}
            />
          </div>
          
          <div>
            <label style={{ display: 'block', marginBottom: '4px', fontWeight: 'bold' }}>{t('wifiPassword')}:</label>
            <input 
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)}
              style={{ 
                width: '100%', 
                padding: '8px', 
                border: '2px solid black',
                fontFamily: 'inherit',
                fontSize: '16px'
              }}
              placeholder={t('enterPassword')}
            />
          </div>

          <button 
            onClick={sendConfig}
            disabled={!device}
            style={{
              background: device ? 'black' : '#ccc',
              color: device ? 'white' : '#666',
              border: '2px solid black',
              padding: '12px',
              fontFamily: 'inherit',
              fontWeight: 'bold',
              cursor: device ? 'pointer' : 'not-allowed',
              marginTop: '8px'
            }}
          >
            {t('sendConfig')}
          </button>
        </div>

        <div style={{ 
          marginTop: '16px', 
          border: '2px solid black', 
          padding: '8px', 
          height: '150px', 
          overflowY: 'auto',
          background: 'white',
          fontFamily: 'monospace',
          fontSize: '12px'
        }}>
          {logs.map((log, i) => (
            <div key={i}>{log}</div>
          ))}
        </div>
      </div>
    </MacWindow>
  );
};
