import React, { useState, useEffect, useRef } from 'react';
import { AppleIcon } from './Icons';
import { useLanguage } from '../contexts/LanguageContext';
import { useModal } from '../contexts/ModalContext';
import { type TranslationKey } from '../i18n';

interface MenuItem {
  label: string;
  action?: () => void;
  disabled?: boolean;
  shortcut?: string;
  separator?: boolean;
}

interface MenuBarProps {
  onOpenApp?: (appId: string) => void;
}

export const MenuBar: React.FC<MenuBarProps> = ({ onOpenApp }) => {
  const { t } = useLanguage();
  const { showAlert } = useModal();
  const [time, setTime] = useState(new Date());
  const [activeMenu, setActiveMenu] = useState<string | null>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setActiveMenu(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleMenuClick = (menuName: string) => {
    setActiveMenu(activeMenu === menuName ? null : menuName);
  };

  const handleItemClick = (action?: () => void) => {
    if (action) action();
    setActiveMenu(null);
  };

  const showNotImplemented = () => {
    showAlert("This feature is not implemented in the demo.", "Not Implemented");
  };

  const menus: Record<string, MenuItem[]> = {
    apple: [
      { label: t('about'), action: () => showAlert("Luna 2025 Mobile\nVersion 1.0.0\n\nCreated for Christmas Special", "About") },
    ],
    file: [
      { label: t('new'), action: showNotImplemented, shortcut: '⌘N' },
      { label: t('open'), action: showNotImplemented, shortcut: '⌘O' },
      { label: t('close'), action: showNotImplemented, shortcut: '⌘W' },
      { separator: true, label: '' },
      { label: t('save'), action: showNotImplemented, shortcut: '⌘S' },
      { label: t('print'), action: showNotImplemented, shortcut: '⌘P' },
      { separator: true, label: '' },
      { label: t('quit'), action: showNotImplemented, shortcut: '⌘Q' },
    ],
    edit: [
      { label: t('undo'), action: showNotImplemented, shortcut: '⌘Z' },
      { separator: true, label: '' },
      { label: t('cut'), action: showNotImplemented, shortcut: '⌘X' },
      { label: t('copy'), action: showNotImplemented, shortcut: '⌘C' },
      { label: t('paste'), action: showNotImplemented, shortcut: '⌘V' },
      { label: t('selectAll'), action: showNotImplemented, shortcut: '⌘A' },
      { separator: true, label: '' },
      { label: t('showClipboard'), action: showNotImplemented },
    ],
    view: [
      { label: t('byIcon'), action: showNotImplemented },
      { label: t('byName'), action: showNotImplemented },
      { label: t('byDate'), action: showNotImplemented },
    ],
    special: [
      { label: t('cleanUp'), action: showNotImplemented },
      { label: t('emptyTrash'), action: () => showAlert(t('trashEmpty'), "Trash") },
      { separator: true, label: '' },
      { label: t('wifiConfig'), action: () => onOpenApp && onOpenApp('wifi') },
      { separator: true, label: '' },
      { label: t('restart'), action: () => window.location.reload() },
      { label: t('shutdown'), action: () => showAlert("It is now safe to turn off your computer.", "Shut Down") },
    ],
  };

  const renderDropdown = (items: MenuItem[]) => (
    <div style={{
      position: 'absolute',
      top: '28px',
      left: 0,
      background: 'white',
      border: '2px solid black',
      boxShadow: '4px 4px 0px 0px rgba(0,0,0,0.5)',
      minWidth: '200px',
      zIndex: 2000,
      display: 'flex',
      flexDirection: 'column',
      padding: '4px 0'
    }}>
      {items.map((item, index) => (
        item.separator ? (
          <div key={index} style={{ borderBottom: '1px dotted black', margin: '4px 0' }} />
        ) : (
          <div
            key={index}
            onClick={() => !item.disabled && handleItemClick(item.action)}
            className="menu-item"
            style={{
              padding: '4px 16px',
              cursor: item.disabled ? 'default' : 'pointer',
              opacity: item.disabled ? 0.5 : 1,
              display: 'flex',
              justifyContent: 'space-between',
              fontFamily: 'var(--mac-font)',
              fontSize: '14px',
            }}
            onMouseEnter={(e) => {
                if (!item.disabled) {
                    e.currentTarget.style.background = 'black';
                    e.currentTarget.style.color = 'white';
                }
            }}
            onMouseLeave={(e) => {
                if (!item.disabled) {
                    e.currentTarget.style.background = 'white';
                    e.currentTarget.style.color = 'black';
                }
            }}
          >
            <span>{item.label}</span>
            {item.shortcut && <span>{item.shortcut}</span>}
          </div>
        )
      ))}
    </div>
  );

  return (
    <div 
      ref={menuRef}
      className="menu-bar"
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '28px',
        background: 'white',
        borderBottom: '2px solid black',
        display: 'flex',
        alignItems: 'center',
        padding: '0 8px',
        justifyContent: 'space-between',
        zIndex: 1000,
        fontFamily: 'var(--mac-font)',
        fontSize: '14px',
        userSelect: 'none'
      }}
    >
      <div className="menu-bar-left" style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
        <div style={{ position: 'relative' }}>
            <div 
                className="menu-item-trigger"
                style={{ padding: '0 8px', cursor: 'pointer', background: activeMenu === 'apple' ? 'black' : 'transparent', color: activeMenu === 'apple' ? 'white' : 'black' }}
                onClick={() => handleMenuClick('apple')}
            >
            <AppleIcon size={16} />
            </div>
            {activeMenu === 'apple' && renderDropdown(menus.apple)}
        </div>

        {['file', 'edit', 'view', 'special'].map(menu => (
            <div key={menu} style={{ position: 'relative' }}>
                <div 
                    className="menu-item-trigger"
                    style={{ padding: '0 8px', cursor: 'pointer', fontWeight: 'bold', background: activeMenu === menu ? 'black' : 'transparent', color: activeMenu === menu ? 'white' : 'black' }}
                    onClick={() => handleMenuClick(menu)}
                >
                    {t(menu as TranslationKey)}
                </div>
                {activeMenu === menu && renderDropdown(menus[menu])}
            </div>
        ))}
      </div>
      <div className="menu-bar-right" style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
        <div className="menu-hd" style={{ cursor: 'pointer' }}>{t('hd')}</div>
        <div>{time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
      </div>
    </div>
  );
};
