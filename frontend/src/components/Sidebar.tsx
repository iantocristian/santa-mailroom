import { Link, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { useNotificationsStore } from '../store/notificationsStore';

interface SidebarProps {
    isOpen?: boolean;
    onClose?: () => void;
}

export default function Sidebar({ isOpen = true, onClose = () => { } }: SidebarProps) {
    const location = useLocation();
    const { user, logout } = useAuthStore();
    const { unreadCount } = useNotificationsStore();

    const navItems = [
        { path: '/', icon: '🏠', label: 'Dashboard' },
        { path: '/children', icon: '👧', label: 'Children' },
        { path: '/wishlist', icon: '🎁', label: 'Wishlist' },
        { path: '/letters', icon: '✉️', label: 'Letters' },
        { path: '/timeline', icon: '📖', label: 'Scrapbook' },
        { path: '/deeds', icon: '⭐', label: 'Good Deeds' },
    ];

    const settingsItems = [
        { path: '/moderation', icon: '🛡️', label: 'Moderation', badge: unreadCount > 0 ? undefined : undefined },
        { path: '/settings', icon: '⚙️', label: 'Settings' },
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
                        <span>Santa's Mailroom</span>
                    </div>
                </div>

                <nav className="sidebar-nav">
                    <div className="nav-section">
                        <div className="nav-section-title">Main</div>
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
                        <div className="nav-section-title">Manage</div>
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
                        <div className="user-name">{user?.name || 'Parent'}</div>
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
