import { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useFamilyStore } from '../store/familyStore';
import { useChildrenStore } from '../store/childrenStore';
import { useNotificationsStore } from '../store/notificationsStore';

export default function Dashboard() {
    const { family, stats, fetchFamily, fetchStats } = useFamilyStore();
    const { children, fetchChildren } = useChildrenStore();
    const { notifications, fetchNotifications } = useNotificationsStore();

    useEffect(() => {
        fetchFamily();
        fetchStats();
        fetchChildren();
        fetchNotifications();
    }, [fetchFamily, fetchStats, fetchChildren, fetchNotifications]);

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
    };

    return (
        <div className="page-content">
            <div className="page-header" style={{ marginBottom: 32, padding: 0, border: 'none', background: 'transparent' }}>
                <h1 className="page-title">
                    <span className="title-icon">🎅</span>
                    Santa's Dashboard
                </h1>
            </div>

            {/* Santa Email Banner */}
            {family?.santa_email && (
                <div className="santa-email-banner" style={{
                    background: 'linear-gradient(135deg, #1a472a 0%, #2d5a3f 50%, #1a472a 100%)',
                    borderRadius: 16,
                    padding: '24px 32px',
                    marginBottom: 32,
                    display: 'flex',
                    alignItems: 'center',
                    gap: 24,
                    boxShadow: '0 8px 32px rgba(0,0,0,0.2)',
                    border: '2px solid rgba(212, 175, 55, 0.3)'
                }}>
                    <div style={{ fontSize: 64, lineHeight: 1 }}>🎅</div>
                    <div style={{ flex: 1 }}>
                        <div style={{
                            fontSize: '0.85rem',
                            color: 'rgba(255,255,255,0.7)',
                            marginBottom: 6,
                            textTransform: 'uppercase',
                            letterSpacing: 1
                        }}>
                            ✉️ Tell your children to send their wish lists to Santa at:
                        </div>
                        <div style={{
                            fontSize: '1.4rem',
                            fontWeight: 700,
                            color: '#d4af37',
                            fontFamily: 'monospace',
                            letterSpacing: 0.5
                        }}>
                            {family.santa_email}
                        </div>
                        <div style={{
                            fontSize: '0.8rem',
                            color: 'rgba(255,255,255,0.5)',
                            marginTop: 6
                        }}>
                            Family Code: <strong style={{ color: 'rgba(255,255,255,0.8)' }}>{family.santa_code}</strong>
                        </div>
                    </div>
                    <button
                        onClick={() => copyToClipboard(family.santa_email || '')}
                        className="btn btn-primary"
                        style={{
                            background: 'rgba(212, 175, 55, 0.2)',
                            border: '1px solid #d4af37',
                            color: '#d4af37'
                        }}
                    >
                        📋 Copy Email
                    </button>
                </div>
            )}

            {/* Stats Grid */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-icon green">👧</div>
                    <div className="stat-content">
                        <div className="stat-value">{stats?.total_children ?? 0}</div>
                        <div className="stat-label">Children</div>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon red">✉️</div>
                    <div className="stat-content">
                        <div className="stat-value">{stats?.total_letters ?? 0}</div>
                        <div className="stat-label">Letters</div>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon gold">🎁</div>
                    <div className="stat-content">
                        <div className="stat-value">{stats?.total_wish_items ?? 0}</div>
                        <div className="stat-label">Wishes</div>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon green">⭐</div>
                    <div className="stat-content">
                        <div className="stat-value">{stats?.completed_deeds ?? 0}</div>
                        <div className="stat-label">Good Deeds</div>
                    </div>
                </div>
            </div>

            {/* Main Content Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 24 }}>
                {/* Children Section */}
                <div className="card">
                    <div className="card-header">
                        <h2 className="card-title">
                            <span>👧</span> Your Children
                        </h2>
                        <Link to="/children" className="btn btn-sm btn-primary">+ Add Child</Link>
                    </div>
                    <div className="card-body">
                        {children.length === 0 ? (
                            <div className="empty-state">
                                <div className="empty-state-icon">🧒</div>
                                <h3>No children registered yet</h3>
                                <p>Add your first child to get started with Santa's mailroom!</p>
                                <Link to="/children" className="btn btn-primary">Add Your First Child</Link>
                            </div>
                        ) : (
                            <div className="children-grid">
                                {children.map((child) => (
                                    <div key={child.id} className="child-card">
                                        <div className="child-header">
                                            <div className="child-avatar">
                                                {child.avatar_url ? (
                                                    <img src={child.avatar_url} alt={child.name} />
                                                ) : (
                                                    '🧒'
                                                )}
                                            </div>
                                            <div>
                                                <div className="child-name">{child.name}</div>
                                                <div className="child-meta">
                                                    {child.country && <span>{child.country} </span>}
                                                    {child.birth_year && (
                                                        <span>• {new Date().getFullYear() - child.birth_year} years old</span>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                        <div className="child-stats">
                                            <div className="child-stat">
                                                <div className="child-stat-value">{child.letter_count ?? 0}</div>
                                                <div className="child-stat-label">Letters</div>
                                            </div>
                                            <div className="child-stat">
                                                <div className="child-stat-value">{child.wish_item_count ?? 0}</div>
                                                <div className="child-stat-label">Wishes</div>
                                            </div>
                                            <div className="child-stat">
                                                <div className="child-stat-value">{child.completed_deeds ?? 0}</div>
                                                <div className="child-stat-label">Deeds</div>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* Notifications Section */}
                <div className="card">
                    <div className="card-header">
                        <h2 className="card-title">
                            <span>🔔</span> Recent Activity
                        </h2>
                    </div>
                    <div className="card-body" style={{ padding: 0 }}>
                        {notifications.length === 0 ? (
                            <div className="empty-state" style={{ padding: 40 }}>
                                <div className="empty-state-icon">🔔</div>
                                <h3>No notifications yet</h3>
                                <p>New letters and alerts will appear here!</p>
                            </div>
                        ) : (
                            <div style={{ maxHeight: 400, overflow: 'auto' }}>
                                {notifications.slice(0, 10).map((notification) => (
                                    <div
                                        key={notification.id}
                                        style={{
                                            padding: '14px 20px',
                                            borderBottom: '1px solid var(--border-secondary)',
                                            background: notification.read ? 'transparent' : 'rgba(212, 175, 55, 0.05)',
                                        }}
                                    >
                                        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 4 }}>
                                            <span>
                                                {notification.type === 'new_letter' && '✉️'}
                                                {notification.type === 'moderation_flag' && '⚠️'}
                                                {notification.type === 'budget_alert' && '💰'}
                                                {notification.type === 'deed_completed' && '⭐'}
                                            </span>
                                            <strong style={{ fontSize: '0.9rem' }}>{notification.title}</strong>
                                        </div>
                                        {notification.message && (
                                            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', margin: 0 }}>
                                                {notification.message}
                                            </p>
                                        )}
                                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: 6 }}>
                                            {new Date(notification.created_at).toLocaleDateString()}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Moderation Alerts */}
            {stats && stats.pending_moderation_flags > 0 && (
                <div className="alert-banner warning" style={{ marginTop: 24 }}>
                    <span>⚠️</span>
                    <div>
                        <strong>{stats.pending_moderation_flags} letter(s) need review</strong>
                        <p style={{ margin: 0, fontSize: '0.9rem' }}>
                            Some letters have been flagged for concerning content.
                        </p>
                    </div>
                    <Link to="/moderation" className="btn btn-sm btn-secondary" style={{ marginLeft: 'auto' }}>
                        Review Now
                    </Link>
                </div>
            )}

            {/* Budget Alert */}
            {stats && stats.total_estimated_budget && stats.total_estimated_budget > 500 && (
                <div className="alert-banner info" style={{ marginTop: 16 }}>
                    <span>💰</span>
                    <div>
                        <strong>Budget Update</strong>
                        <p style={{ margin: 0, fontSize: '0.9rem' }}>
                            Total estimated wishlist cost: ${stats.total_estimated_budget.toFixed(2)}
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
}
