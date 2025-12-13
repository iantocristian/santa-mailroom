import { Link, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuthStore } from '../store/authStore';
import { useNotificationsStore } from '../store/notificationsStore';

interface SidebarProps {
    isOpen?: boolean;
    onClose?: () => void;
}

export default function Sidebar({ isOpen = true, onClose = () => { } }: SidebarProps) {
    const { t } = useTranslation();
    const location = useLocation();
    const { user, logout } = useAuthStore();
    const { unreadCount } = useNotificationsStore();

    const navItems = [
        { path: '/', icon: '🏠', label: t('sidebar.dashboard') },
        { path: '/children', icon: '👧', label: t('sidebar.children') },
        { path: '/wishlist', icon: '🎁', label: t('sidebar.wishlist') },
        { path: '/letters', icon: '✉️', label: t('sidebar.letters') },
        { path: '/timeline', icon: '📖', label: t('sidebar.scrapbook') },
        { path: '/deeds', icon: '⭐', label: t('sidebar.goodDeeds') },
        { path: '/sent-emails', icon: '📤', label: t('sidebar.sentEmails') },
    ];

    const settingsItems = [
        { path: '/moderation', icon: '🛡️', label: t('sidebar.moderation'), badge: unreadCount > 0 ? undefined : undefined },
        { path: '/settings', icon: '⚙️', label: t('sidebar.settings') },
    ];

    const isActive = (path: string) => location.pathname === path;

    return (
        <>
            {/* Mobile overlay - hidden on desktop via CSS */}
            <div
                className={`sidebar-overlay ${isOpen ? 'visible' : ''}`}
                onClick={onClose}
            />

            <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
                <div className="sidebar-header">
                    <div className="sidebar-logo">
                        <span className="logo-icon">🎅</span>
                        <span>{t('sidebar.appName')}</span>
                    </div>
                </div>

                <nav className="sidebar-nav">
                    <div className="nav-section">
                        <div className="nav-section-title">{t('sidebar.main')}</div>
                        {navItems.map((item) => (
                            <Link
                                key={item.path}
                                to={item.path}
                                className={`nav-item ${isActive(item.path) ? 'active' : ''}`}
                                onClick={onClose}
                            >
                                <span className="nav-icon">{item.icon}</span>
                                <span>{item.label}</span>
                            </Link>
                        ))}
                    </div>

                    <div className="nav-section">
                        <div className="nav-section-title">{t('sidebar.manage')}</div>
                        {settingsItems.map((item) => (
                            <Link
                                key={item.path}
                                to={item.path}
                                className={`nav-item ${isActive(item.path) ? 'active' : ''}`}
                                onClick={onClose}
                            >
                                <span className="nav-icon">{item.icon}</span>
                                <span>{item.label}</span>
                            </Link>
                        ))}
                    </div>
                </nav>

                <div className="sidebar-user">
                    <div className="user-avatar">
                        {user?.name?.[0]?.toUpperCase() || user?.email?.[0]?.toUpperCase() || '?'}
                    </div>
                    <div className="user-info">
                        <div className="user-name">{user?.name || t('sidebar.parent')}</div>
                        <div className="user-email">{user?.email}</div>
                    </div>
                    <button className="logout-btn" onClick={logout} title="Logout">
                        🚪
                    </button>
                </div>
            </aside>
        </>
    );
}
