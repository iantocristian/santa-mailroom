import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useFamilyStore } from '../store/familyStore';
import { useChildrenStore } from '../store/childrenStore';
import { useNotificationsStore } from '../store/notificationsStore';

export default function Dashboard() {
    const { t } = useTranslation();
    const { family, stats, fetchFamily, fetchStats } = useFamilyStore();
    const { children, fetchChildren } = useChildrenStore();
    const { notifications, fetchNotifications } = useNotificationsStore();
    const [copyStatus, setCopyStatus] = useState<'idle' | 'copied' | 'error'>('idle');

    useEffect(() => {
        fetchFamily();
        fetchStats();
        fetchChildren();
        fetchNotifications();
    }, [fetchFamily, fetchStats, fetchChildren, fetchNotifications]);

    const copyToClipboard = async (text: string) => {
        try {
            await navigator.clipboard.writeText(text);
            setCopyStatus('copied');
            setTimeout(() => setCopyStatus('idle'), 2000);
        } catch (err) {
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            document.body.appendChild(textArea);
            textArea.select();
            try {
                document.execCommand('copy');
                setCopyStatus('copied');
                setTimeout(() => setCopyStatus('idle'), 2000);
            } catch (e) {
                setCopyStatus('error');
                setTimeout(() => setCopyStatus('idle'), 2000);
            }
            document.body.removeChild(textArea);
        }
    };

    return (
        <div className="page-content">
            <div className="page-header" style={{ marginBottom: 32, padding: 0, border: 'none', background: 'transparent' }}>
                <h1 className="page-title">
                    <span className="title-icon">🎅</span>
                    {t('dashboard.title')}
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
                    <div className="santa-icon-large" style={{ fontSize: 64, lineHeight: 1 }}>🎅</div>
                    <div style={{ flex: 1 }}>
                        <div className="santa-email-label" style={{
                            fontSize: '0.85rem',
                            color: 'rgba(255,255,255,0.7)',
                            marginBottom: 6,
                            textTransform: 'uppercase',
                            letterSpacing: 1
                        }}>
                            ✉️ {t('dashboard.sendEmailTo')}
                        </div>
                        <div className="santa-email-address" style={{
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
                            {t('dashboard.familyCode')} <strong style={{ color: 'rgba(255,255,255,0.8)' }}>{family.santa_code}</strong>
                        </div>
                    </div>
                    <button
                        onClick={() => copyToClipboard(family.santa_email || '')}
                        className="btn btn-primary"
                        style={{
                            background: copyStatus === 'copied' ? 'rgba(34, 197, 94, 0.2)' :
                                copyStatus === 'error' ? 'rgba(239, 68, 68, 0.2)' :
                                    'rgba(212, 175, 55, 0.2)',
                            border: copyStatus === 'copied' ? '1px solid #22c55e' :
                                copyStatus === 'error' ? '1px solid #ef4444' :
                                    '1px solid #d4af37',
                            color: copyStatus === 'copied' ? '#22c55e' :
                                copyStatus === 'error' ? '#ef4444' :
                                    '#d4af37',
                            transition: 'all 0.2s ease'
                        }}
                    >
                        {copyStatus === 'copied' ? `✓ ${t('dashboard.copied')}` :
                            copyStatus === 'error' ? `⚠️ ${t('dashboard.copyFailed')}` :
                                `📋 ${t('dashboard.copyEmail')}`}
                    </button>
                </div>
            )}

            {/* Stats Grid */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-icon green">👧</div>
                    <div className="stat-content">
                        <div className="stat-value">{stats?.total_children ?? 0}</div>
                        <div className="stat-label">{t('dashboard.children')}</div>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon red">✉️</div>
                    <div className="stat-content">
                        <div className="stat-value">{stats?.total_letters ?? 0}</div>
                        <div className="stat-label">{t('dashboard.letters')}</div>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon gold">🎁</div>
                    <div className="stat-content">
                        <div className="stat-value">{stats?.total_wish_items ?? 0}</div>
                        <div className="stat-label">{t('dashboard.wishes')}</div>
                    </div>
                </div>

                <div className="stat-card">
                    <div className="stat-icon green">⭐</div>
                    <div className="stat-content">
                        <div className="stat-value">{stats?.completed_deeds ?? 0}</div>
                        <div className="stat-label">{t('dashboard.goodDeeds')}</div>
                    </div>
                </div>
            </div>

            {/* Main Content Grid */}
            <div className="dashboard-grid" style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 24 }}>
                {/* Children Section */}
                <div className="card">
                    <div className="card-header">
                        <h2 className="card-title">
                            <span>👧</span> {t('dashboard.yourChildren')}
                        </h2>
                        <Link to="/children" className="btn btn-sm btn-primary">+ {t('dashboard.addChild')}</Link>
                    </div>
                    <div className="card-body">
                        {children.length === 0 ? (
                            <div className="empty-state">
                                <div className="empty-state-icon">🧒</div>
                                <h3>{t('dashboard.noChildrenYet')}</h3>
                                <p>{t('dashboard.addFirstChildDesc')}</p>
                                <Link to="/children" className="btn btn-primary">{t('dashboard.addFirstChild')}</Link>
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
                                                        <span>• {new Date().getFullYear() - child.birth_year} {t('common.yearsOld')}</span>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                        <div className="child-stats">
                                            <div className="child-stat">
                                                <div className="child-stat-value">{child.letter_count ?? 0}</div>
                                                <div className="child-stat-label">{t('children.letters')}</div>
                                            </div>
                                            <div className="child-stat">
                                                <div className="child-stat-value">{child.wish_item_count ?? 0}</div>
                                                <div className="child-stat-label">{t('children.wishes')}</div>
                                            </div>
                                            <div className="child-stat">
                                                <div className="child-stat-value">{child.completed_deeds ?? 0}</div>
                                                <div className="child-stat-label">{t('children.deeds')}</div>
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
                            <span>🔔</span> {t('dashboard.recentActivity')}
                        </h2>
                    </div>
                    <div className="card-body" style={{ padding: 0 }}>
                        {notifications.length === 0 ? (
                            <div className="empty-state" style={{ padding: 40 }}>
                                <div className="empty-state-icon">🔔</div>
                                <h3>{t('dashboard.noNotifications')}</h3>
                                <p>{t('dashboard.notificationsDesc')}</p>
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
                        <strong>{t('dashboard.lettersNeedReview', { count: stats.pending_moderation_flags })}</strong>
                        <p style={{ margin: 0, fontSize: '0.9rem' }}>
                            {t('dashboard.moderationDesc')}
                        </p>
                    </div>
                    <Link to="/moderation" className="btn btn-sm btn-secondary" style={{ marginLeft: 'auto' }}>
                        {t('dashboard.reviewNow')}
                    </Link>
                </div>
            )}

            {/* Budget Alert */}
            {stats && stats.total_estimated_budget && stats.total_estimated_budget > 500 && (
                <div className="alert-banner info" style={{ marginTop: 16 }}>
                    <span>💰</span>
                    <div>
                        <strong>{t('dashboard.budgetUpdate')}</strong>
                        <p style={{ margin: 0, fontSize: '0.9rem' }}>
                            {t('dashboard.totalEstimatedCost', { amount: `$${stats.total_estimated_budget.toFixed(2)}` })}
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
}
