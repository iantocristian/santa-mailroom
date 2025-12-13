import { useState, useEffect, FormEvent } from 'react';
import { useTranslation } from 'react-i18next';
import { useChildrenStore } from '../store/childrenStore';
import { COUNTRIES } from '../constants/countries';
import { LANGUAGES } from '../constants/languages';
import type { ChildCreate } from '../types';

export default function ChildrenPage() {
    const { t } = useTranslation();
    const { children, isLoading, fetchChildren, addChild, deleteChild } = useChildrenStore();
    const [showModal, setShowModal] = useState(false);
    const [formData, setFormData] = useState<ChildCreate>({
        name: '',
        email: '',
        country: '',
        birth_year: undefined,
        language: '',
    });
    const [error, setError] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    useEffect(() => {
        fetchChildren();
    }, [fetchChildren]);

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        setError('');
        setIsSubmitting(true);

        try {
            await addChild(formData);
            setShowModal(false);
            setFormData({ name: '', email: '', country: '', birth_year: undefined, language: '' });
        } catch (err: unknown) {
            const error = err as { response?: { data?: { detail?: string | Array<{ msg: string }> } } };
            const detail = error.response?.data?.detail;
            if (typeof detail === 'string') {
                setError(detail);
            } else if (Array.isArray(detail)) {
                setError(detail.map(e => e.msg).join(', '));
            } else {
                setError(t('children.failedToAdd'));
            }
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleDelete = async (id: number, name: string) => {
        if (confirm(t('children.confirmDelete', { name }))) {
            await deleteChild(id);
        }
    };

    const calculateAge = (birthYear?: number | null) => {
        if (!birthYear) return null;
        return new Date().getFullYear() - birthYear;
    };

    return (
        <div className="page-content">
            <div className="page-header" style={{ marginBottom: 32, padding: 0, border: 'none', background: 'transparent' }}>
                <h1 className="page-title">
                    <span className="title-icon">👧</span>
                    {t('children.title')}
                </h1>
                <button className="btn btn-primary" onClick={() => setShowModal(true)}>
                    ✨ {t('children.addChild')}
                </button>
            </div>

            {isLoading ? (
                <div style={{ textAlign: 'center', padding: 60 }}>
                    <div className="spinner" style={{ margin: '0 auto' }} />
                    <p style={{ color: 'var(--text-secondary)', marginTop: 16 }}>{t('common.loading')}</p>
                </div>
            ) : children.length === 0 ? (
                <div className="card">
                    <div className="card-body">
                        <div className="empty-state">
                            <div className="empty-state-icon">👧</div>
                            <h3>{t('children.noChildrenYet')}</h3>
                            <p>{t('children.addFirstChildDesc')}</p>
                            <button className="btn btn-primary" onClick={() => setShowModal(true)}>
                                {t('children.addFirstChild')}
                            </button>
                        </div>
                    </div>
                </div>
            ) : (
                <div className="children-grid">
                    {children.map((child) => (
                        <div key={child.id} className="child-card">
                            <div className="child-header">
                                <div className="child-avatar">
                                    {child.avatar_url ? (
                                        <img src={child.avatar_url} alt={child.name} style={{ width: '100%', height: '100%', borderRadius: '50%', objectFit: 'cover' }} />
                                    ) : (
                                        '🧒'
                                    )}
                                </div>
                                <div style={{ flex: 1 }}>
                                    <div className="child-name">{child.name}</div>
                                    <div className="child-meta">
                                        {child.country && <span>{child.country}</span>}
                                        {child.birth_year && (
                                            <span>{child.country ? ' • ' : ''}{calculateAge(child.birth_year)} {t('common.yearsOld')}</span>
                                        )}
                                    </div>
                                </div>
                                <button
                                    className="btn btn-icon btn-secondary"
                                    onClick={() => handleDelete(child.id, child.name)}
                                    title={t('children.removeChild')}
                                    style={{ width: 32, height: 32, padding: 0, fontSize: '0.85rem' }}
                                >
                                    🗑️
                                </button>
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

            {/* Add Child Modal */}
            {showModal && (
                <div
                    style={{
                        position: 'fixed',
                        inset: 0,
                        background: 'rgba(0,0,0,0.7)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        zIndex: 1000,
                        padding: 20,
                    }}
                    onClick={() => setShowModal(false)}
                >
                    <div
                        className="card"
                        style={{ maxWidth: 480, width: '100%' }}
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div className="card-header">
                            <h2 className="card-title">
                                <span>✨</span> {t('children.addChildTitle')}
                            </h2>
                            <button
                                className="btn btn-icon btn-secondary"
                                onClick={() => setShowModal(false)}
                                style={{ width: 32, height: 32, padding: 0 }}
                            >
                                ✕
                            </button>
                        </div>
                        <form onSubmit={handleSubmit}>
                            <div className="card-body">
                                {error && <div className="auth-error" style={{ marginBottom: 16 }}>{error}</div>}

                                <div className="form-group">
                                    <label className="form-label">{t('children.childName')} *</label>
                                    <input
                                        type="text"
                                        className="form-input"
                                        placeholder="e.g., Emma"
                                        value={formData.name}
                                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                        required
                                        autoFocus
                                    />
                                </div>

                                <div className="form-group">
                                    <label className="form-label">{t('children.childEmail')} *</label>
                                    <input
                                        type="email"
                                        className="form-input"
                                        placeholder={t('children.childEmailPlaceholder')}
                                        value={formData.email}
                                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                        required
                                    />
                                    <small style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                                        {t('children.emailPrivacyNote')}
                                    </small>
                                </div>

                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                                    <div className="form-group">
                                        <label className="form-label">{t('children.country')}</label>
                                        <select
                                            className="form-input"
                                            value={formData.country || ''}
                                            onChange={(e) => setFormData({ ...formData, country: e.target.value || undefined })}
                                        >
                                            <option value="">{t('children.selectCountry')}</option>
                                            {COUNTRIES.map(c => (
                                                <option key={c.code} value={c.code}>{c.name}</option>
                                            ))}
                                        </select>
                                    </div>

                                    <div className="form-group">
                                        <label className="form-label">{t('children.birthYear')}</label>
                                        <input
                                            type="number"
                                            className="form-input"
                                            placeholder="e.g., 2016"
                                            value={formData.birth_year || ''}
                                            onChange={(e) => setFormData({ ...formData, birth_year: e.target.value ? parseInt(e.target.value) : undefined })}
                                            min={2000}
                                            max={new Date().getFullYear()}
                                        />
                                    </div>
                                </div>

                                <div className="form-group">
                                    <label className="form-label">{t('children.emailLanguage')} 🌍</label>
                                    <select
                                        className="form-input"
                                        value={formData.language || ''}
                                        onChange={(e) => setFormData({ ...formData, language: e.target.value || undefined })}
                                    >
                                        <option value="">{t('children.englishDefault')}</option>
                                        {LANGUAGES.filter(l => l.code !== 'en').map(l => (
                                            <option key={l.code} value={l.code}>{l.name} ({l.native})</option>
                                        ))}
                                    </select>
                                    <small style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                                        {t('children.santaLanguageNote')}
                                    </small>
                                </div>
                            </div>

                            <div style={{ padding: '16px 24px', borderTop: '1px solid var(--border-secondary)', display: 'flex', gap: 12, justifyContent: 'flex-end' }}>
                                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                                    {t('common.cancel')}
                                </button>
                                <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
                                    {isSubmitting ? '...' : `🎄 ${t('children.addChild')}`}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
