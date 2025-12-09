import { useState, useEffect, FormEvent } from 'react';
import { useDeedsStore } from '../store/deedsStore';
import { useChildrenStore } from '../store/childrenStore';

export default function GoodDeedsPage() {
    const { deeds, isLoading, fetchDeeds, createDeed, completeDeed, deleteDeed } = useDeedsStore();
    const { children, fetchChildren } = useChildrenStore();
    const [selectedChild, setSelectedChild] = useState<number | undefined>();
    const [showCompleted, setShowCompleted] = useState<boolean | undefined>();
    const [showModal, setShowModal] = useState(false);
    const [showCompleteModal, setShowCompleteModal] = useState<number | null>(null);
    const [newDeed, setNewDeed] = useState({ child_id: 0, description: '' });
    const [completeNote, setCompleteNote] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    useEffect(() => {
        fetchChildren();
    }, [fetchChildren]);

    useEffect(() => {
        fetchDeeds({ child_id: selectedChild, completed: showCompleted });
    }, [fetchDeeds, selectedChild, showCompleted]);

    const getChildName = (childId: number) => {
        return children.find(c => c.id === childId)?.name || 'Unknown';
    };

    const handleCreateDeed = async (e: FormEvent) => {
        e.preventDefault();
        if (!newDeed.child_id || !newDeed.description.trim()) return;

        setIsSubmitting(true);
        try {
            await createDeed(newDeed.child_id, newDeed.description);
            setShowModal(false);
            setNewDeed({ child_id: 0, description: '' });
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleComplete = async () => {
        if (showCompleteModal === null) return;

        setIsSubmitting(true);
        try {
            await completeDeed(showCompleteModal, completeNote || undefined);
            setShowCompleteModal(null);
            setCompleteNote('');
        } finally {
            setIsSubmitting(false);
        }
    };

    const pendingDeeds = deeds.filter(d => !d.completed);
    const completedDeeds = deeds.filter(d => d.completed);

    return (
        <div className="page-content">
            <div className="page-header" style={{ marginBottom: 24, padding: 0, border: 'none', background: 'transparent' }}>
                <h1 className="page-title">
                    <span className="title-icon">⭐</span>
                    Good Deeds Tracker
                </h1>
                <button className="btn btn-primary" onClick={() => setShowModal(true)}>
                    + Add Deed
                </button>
            </div>

            {/* Filters */}
            <div className="card" style={{ marginBottom: 24 }}>
                <div className="card-body" style={{ padding: '12px 20px' }}>
                    <div style={{ display: 'flex', gap: 16, alignItems: 'center', flexWrap: 'wrap' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                            <label style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Child:</label>
                            <select
                                className="form-input"
                                style={{ width: 'auto', padding: '6px 12px' }}
                                value={selectedChild || ''}
                                onChange={(e) => setSelectedChild(e.target.value ? parseInt(e.target.value) : undefined)}
                            >
                                <option value="">All Children</option>
                                {children.map(child => (
                                    <option key={child.id} value={child.id}>{child.name}</option>
                                ))}
                            </select>
                        </div>

                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                            <label style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Status:</label>
                            <select
                                className="form-input"
                                style={{ width: 'auto', padding: '6px 12px' }}
                                value={showCompleted === undefined ? '' : showCompleted ? 'completed' : 'pending'}
                                onChange={(e) => {
                                    if (e.target.value === '') setShowCompleted(undefined);
                                    else setShowCompleted(e.target.value === 'completed');
                                }}
                            >
                                <option value="">All</option>
                                <option value="pending">Pending</option>
                                <option value="completed">Completed</option>
                            </select>
                        </div>

                        <div style={{ marginLeft: 'auto', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                            {pendingDeeds.length} pending, {completedDeeds.length} completed
                        </div>
                    </div>
                </div>
            </div>

            {/* Deeds List */}
            {isLoading ? (
                <div style={{ textAlign: 'center', padding: 60 }}>
                    <div className="spinner" style={{ margin: '0 auto' }} />
                </div>
            ) : deeds.length === 0 ? (
                <div className="card">
                    <div className="card-body">
                        <div className="empty-state">
                            <div className="empty-state-icon">⭐</div>
                            <h3>No good deeds yet</h3>
                            <p>Santa will suggest good deeds in his replies, or you can add your own!</p>
                            <button className="btn btn-primary" onClick={() => setShowModal(true)}>
                                Add a Good Deed
                            </button>
                        </div>
                    </div>
                </div>
            ) : (
                <div style={{ display: 'grid', gap: 24 }}>
                    {/* Pending Section */}
                    {pendingDeeds.length > 0 && (
                        <div>
                            <h2 style={{ fontSize: '1.1rem', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
                                <span>⏳</span> Pending Deeds ({pendingDeeds.length})
                            </h2>
                            <div style={{ display: 'grid', gap: 12 }}>
                                {pendingDeeds.map(deed => (
                                    <div key={deed.id} className="card">
                                        <div className="card-body" style={{ padding: '16px 20px' }}>
                                            <div style={{ display: 'flex', alignItems: 'flex-start', gap: 16 }}>
                                                <div style={{
                                                    width: 40,
                                                    height: 40,
                                                    borderRadius: '50%',
                                                    background: 'var(--gold)20',
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    justifyContent: 'center',
                                                    fontSize: '1.2rem',
                                                    flexShrink: 0
                                                }}>
                                                    ⭐
                                                </div>
                                                <div style={{ flex: 1 }}>
                                                    <div style={{ fontWeight: 600, marginBottom: 4 }}>
                                                        {deed.description}
                                                    </div>
                                                    <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                                                        👧 {getChildName(deed.child_id)} •
                                                        📅 {new Date(deed.suggested_at).toLocaleDateString()}
                                                    </div>
                                                </div>
                                                <div style={{ display: 'flex', gap: 8 }}>
                                                    <button
                                                        className="btn btn-sm btn-primary"
                                                        onClick={() => setShowCompleteModal(deed.id)}
                                                    >
                                                        ✓ Complete
                                                    </button>
                                                    <button
                                                        className="btn btn-sm btn-secondary"
                                                        onClick={() => deleteDeed(deed.id)}
                                                    >
                                                        ✕
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Completed Section */}
                    {completedDeeds.length > 0 && (
                        <div>
                            <h2 style={{ fontSize: '1.1rem', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
                                <span>✅</span> Completed Deeds ({completedDeeds.length})
                            </h2>
                            <div style={{ display: 'grid', gap: 12 }}>
                                {completedDeeds.map(deed => (
                                    <div key={deed.id} className="card" style={{ opacity: 0.8 }}>
                                        <div className="card-body" style={{ padding: '16px 20px' }}>
                                            <div style={{ display: 'flex', alignItems: 'flex-start', gap: 16 }}>
                                                <div style={{
                                                    width: 40,
                                                    height: 40,
                                                    borderRadius: '50%',
                                                    background: 'var(--green)20',
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    justifyContent: 'center',
                                                    fontSize: '1.2rem',
                                                    flexShrink: 0
                                                }}>
                                                    ✅
                                                </div>
                                                <div style={{ flex: 1 }}>
                                                    <div style={{ fontWeight: 600, marginBottom: 4, textDecoration: 'line-through', opacity: 0.7 }}>
                                                        {deed.description}
                                                    </div>
                                                    <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                                                        👧 {getChildName(deed.child_id)} •
                                                        ✓ Completed {deed.completed_at && new Date(deed.completed_at).toLocaleDateString()}
                                                    </div>
                                                    {deed.parent_note && (
                                                        <div style={{
                                                            marginTop: 8,
                                                            padding: '8px 12px',
                                                            background: 'var(--bg-secondary)',
                                                            borderRadius: 6,
                                                            fontSize: '0.85rem',
                                                            fontStyle: 'italic'
                                                        }}>
                                                            "{deed.parent_note}"
                                                        </div>
                                                    )}
                                                </div>
                                                <button
                                                    className="btn btn-sm btn-secondary"
                                                    onClick={() => deleteDeed(deed.id)}
                                                    style={{ opacity: 0.6 }}
                                                >
                                                    ✕
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Add Deed Modal */}
            {showModal && (
                <div className="modal-overlay" onClick={() => setShowModal(false)}>
                    <div className="modal" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>Add Good Deed</h2>
                            <button className="btn btn-icon" onClick={() => setShowModal(false)}>✕</button>
                        </div>
                        <form onSubmit={handleCreateDeed}>
                            <div className="modal-body">
                                <div className="form-group">
                                    <label className="form-label">Child *</label>
                                    <select
                                        className="form-input"
                                        value={newDeed.child_id || ''}
                                        onChange={(e) => setNewDeed({ ...newDeed, child_id: parseInt(e.target.value) || 0 })}
                                        required
                                    >
                                        <option value="">Select a child...</option>
                                        {children.map(child => (
                                            <option key={child.id} value={child.id}>{child.name}</option>
                                        ))}
                                    </select>
                                </div>
                                <div className="form-group">
                                    <label className="form-label">Good Deed Description *</label>
                                    <textarea
                                        className="form-input"
                                        placeholder="e.g., Help mom with the dishes"
                                        value={newDeed.description}
                                        onChange={(e) => setNewDeed({ ...newDeed, description: e.target.value })}
                                        rows={3}
                                        required
                                    />
                                </div>
                            </div>
                            <div className="modal-footer">
                                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                                    Cancel
                                </button>
                                <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
                                    {isSubmitting ? 'Adding...' : 'Add Deed'}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            {/* Complete Deed Modal */}
            {showCompleteModal !== null && (
                <div className="modal-overlay" onClick={() => setShowCompleteModal(null)}>
                    <div className="modal" onClick={e => e.stopPropagation()}>
                        <div className="modal-header">
                            <h2>🎉 Mark as Complete</h2>
                            <button className="btn btn-icon" onClick={() => setShowCompleteModal(null)}>✕</button>
                        </div>
                        <div className="modal-body">
                            <p style={{ marginBottom: 16 }}>
                                Great job! Add an optional note about how it went:
                            </p>
                            <div className="form-group">
                                <label className="form-label">Parent Note (optional)</label>
                                <textarea
                                    className="form-input"
                                    placeholder="e.g., Did a great job helping!"
                                    value={completeNote}
                                    onChange={(e) => setCompleteNote(e.target.value)}
                                    rows={3}
                                />
                            </div>
                        </div>
                        <div className="modal-footer">
                            <button className="btn btn-secondary" onClick={() => setShowCompleteModal(null)}>
                                Cancel
                            </button>
                            <button className="btn btn-primary" onClick={handleComplete} disabled={isSubmitting}>
                                {isSubmitting ? 'Saving...' : '✓ Mark Complete'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
