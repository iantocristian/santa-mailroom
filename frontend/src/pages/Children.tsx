import { useState, useEffect, FormEvent } from 'react';
import { useChildrenStore } from '../store/childrenStore';
import type { ChildCreate } from '../types';

export default function ChildrenPage() {
    const { children, isLoading, fetchChildren, addChild, deleteChild } = useChildrenStore();
    const [showModal, setShowModal] = useState(false);
    const [formData, setFormData] = useState<ChildCreate>({
        name: '',
        email: '',
        country: '',
        birth_year: undefined,
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
            setFormData({ name: '', email: '', country: '', birth_year: undefined });
        } catch (err: unknown) {
            const error = err as { response?: { data?: { detail?: string } } };
            setError(error.response?.data?.detail || 'Failed to add child');
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleDelete = async (id: number, name: string) => {
        if (confirm(`Are you sure you want to remove ${name}? This will delete all their letters and wishes.`)) {
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
                    Children
                </h1>
                <button className="btn btn-primary" onClick={() => setShowModal(true)}>
                    ✨ Add Child
                </button>
            </div>

            {isLoading ? (
                <div style={{ textAlign: 'center', padding: 60 }}>
                    <div className="spinner" style={{ margin: '0 auto' }} />
                    <p style={{ color: 'var(--text-secondary)', marginTop: 16 }}>Loading...</p>
                </div>
            ) : children.length === 0 ? (
                <div className="card">
                    <div className="card-body">
                        <div className="empty-state">
                            <div className="empty-state-icon">👧</div>
                            <h3>No children registered yet</h3>
                            <p>Add your first child to start receiving letters from Santa's mailroom!</p>
                            <button className="btn btn-primary" onClick={() => setShowModal(true)}>
                                Add Your First Child
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
                                            <span>{child.country ? ' • ' : ''}{calculateAge(child.birth_year)} years old</span>
                                        )}
                                    </div>
                                </div>
                                <button
                                    className="btn btn-icon btn-secondary"
                                    onClick={() => handleDelete(child.id, child.name)}
                                    title="Remove child"
                                    style={{ width: 32, height: 32, padding: 0, fontSize: '0.85rem' }}
                                >
                                    🗑️
                                </button>
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
                                <span>✨</span> Add a Child
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
                                    <label className="form-label">Child's Name *</label>
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
                                    <label className="form-label">Child's Email *</label>
                                    <input
                                        type="email"
                                        className="form-input"
                                        placeholder="The email they'll use to write Santa"
                                        value={formData.email}
                                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                        required
                                    />
                                    <small style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                                        This email will be hashed for privacy. Only emails from registered addresses will be processed.
                                    </small>
                                </div>

                                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
                                    <div className="form-group">
                                        <label className="form-label">Country</label>
                                        <input
                                            type="text"
                                            className="form-input"
                                            placeholder="e.g., USA"
                                            value={formData.country || ''}
                                            onChange={(e) => setFormData({ ...formData, country: e.target.value })}
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label className="form-label">Birth Year</label>
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
                            </div>

                            <div style={{ padding: '16px 24px', borderTop: '1px solid var(--border-secondary)', display: 'flex', gap: 12, justifyContent: 'flex-end' }}>
                                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                                    Cancel
                                </button>
                                <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
                                    {isSubmitting ? '...' : '🎄 Add Child'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
}
