import { useState, useEffect } from 'react';
import { useLettersStore } from '../store/lettersStore';
import { useChildrenStore } from '../store/childrenStore';

export default function LettersPage() {
    const { letters, isLoading, fetchLetters } = useLettersStore();
    const { children, fetchChildren } = useChildrenStore();
    const [selectedChild, setSelectedChild] = useState<number | undefined>();
    const [selectedLetter, setSelectedLetter] = useState<number | null>(null);

    useEffect(() => {
        fetchChildren();
    }, [fetchChildren]);

    useEffect(() => {
        fetchLetters({ child_id: selectedChild });
    }, [fetchLetters, selectedChild]);

    const getChildName = (childId: number) => {
        return children.find(c => c.id === childId)?.name || 'Unknown';
    };

    const formatDate = (dateStr: string) => {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const getStatusBadge = (status: string) => {
        const statusMap: Record<string, { label: string; color: string }> = {
            pending: { label: 'Pending', color: 'var(--gold)' },
            processing: { label: 'Processing', color: 'var(--accent)' },
            processed: { label: 'Processed', color: 'var(--green)' },
            replied: { label: 'Replied', color: 'var(--green)' },
            failed: { label: 'Failed', color: 'var(--red)' },
        };
        const info = statusMap[status] || statusMap.pending;
        return (
            <span style={{
                fontSize: '0.75rem',
                padding: '2px 8px',
                borderRadius: 4,
                background: `${info.color}20`,
                color: info.color
            }}>
                {info.label}
            </span>
        );
    };

    const currentLetter = selectedLetter
        ? letters.find(l => l.id === selectedLetter)
        : null;

    return (
        <div className="page-content">
            <div className="page-header" style={{ marginBottom: 24, padding: 0, border: 'none', background: 'transparent' }}>
                <h1 className="page-title">
                    <span className="title-icon">✉️</span>
                    Letters to Santa
                </h1>
            </div>

            {/* Filters */}
            <div className="card" style={{ marginBottom: 24 }}>
                <div className="card-body" style={{ padding: '12px 20px' }}>
                    <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                            <label style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>From:</label>
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

                        <div style={{ marginLeft: 'auto', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                            {letters.length} letter{letters.length !== 1 ? 's' : ''}
                        </div>
                    </div>
                </div>
            </div>

            {/* Letters Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: selectedLetter ? '1fr 2fr' : '1fr', gap: 24 }}>
                {/* Letter List */}
                <div>
                    {isLoading ? (
                        <div style={{ textAlign: 'center', padding: 60 }}>
                            <div className="spinner" style={{ margin: '0 auto' }} />
                        </div>
                    ) : letters.length === 0 ? (
                        <div className="card">
                            <div className="card-body">
                                <div className="empty-state">
                                    <div className="empty-state-icon">✉️</div>
                                    <h3>No letters yet</h3>
                                    <p>When children email Santa, their letters will appear here!</p>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                            {letters.map(letter => (
                                <div
                                    key={letter.id}
                                    className="card"
                                    style={{
                                        cursor: 'pointer',
                                        borderColor: selectedLetter === letter.id ? 'var(--accent)' : undefined,
                                        transition: 'border-color 0.2s'
                                    }}
                                    onClick={() => setSelectedLetter(letter.id)}
                                >
                                    <div className="card-body" style={{ padding: '14px 18px' }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                                <span style={{ fontSize: '1.2rem' }}>👧</span>
                                                <strong>{getChildName(letter.child_id)}</strong>
                                            </div>
                                            {getStatusBadge(letter.status)}
                                        </div>

                                        {letter.subject && (
                                            <div style={{ fontSize: '0.95rem', marginBottom: 6, fontWeight: 500 }}>
                                                {letter.subject}
                                            </div>
                                        )}

                                        <div style={{
                                            fontSize: '0.85rem',
                                            color: 'var(--text-secondary)',
                                            overflow: 'hidden',
                                            textOverflow: 'ellipsis',
                                            whiteSpace: 'nowrap'
                                        }}>
                                            {letter.body_text?.slice(0, 100)}...
                                        </div>

                                        <div style={{
                                            fontSize: '0.75rem',
                                            color: 'var(--text-muted)',
                                            marginTop: 8,
                                            display: 'flex',
                                            justifyContent: 'space-between'
                                        }}>
                                            <span>📅 {formatDate(letter.received_at)}</span>
                                            <span>🎁 {letter.wish_item_count ?? 0} wishes</span>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Letter Detail */}
                {currentLetter && (
                    <div className="card" style={{ position: 'sticky', top: 20, alignSelf: 'flex-start' }}>
                        <div className="card-header">
                            <h2 className="card-title">
                                <span>📖</span> Letter from {getChildName(currentLetter.child_id)}
                            </h2>
                            <button
                                className="btn btn-icon btn-secondary"
                                onClick={() => setSelectedLetter(null)}
                                style={{ width: 32, height: 32, padding: 0 }}
                            >
                                ✕
                            </button>
                        </div>
                        <div className="card-body">
                            <div style={{ marginBottom: 16 }}>
                                <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: 4 }}>
                                    📅 Received: {formatDate(currentLetter.received_at)}
                                </div>
                                {currentLetter.subject && (
                                    <div style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: 8 }}>
                                        {currentLetter.subject}
                                    </div>
                                )}
                            </div>

                            <div style={{
                                background: 'var(--bg-secondary)',
                                padding: 20,
                                borderRadius: 8,
                                whiteSpace: 'pre-wrap',
                                fontFamily: "'Crimson Text', serif",
                                fontSize: '1.05rem',
                                lineHeight: 1.6,
                                maxHeight: 400,
                                overflow: 'auto'
                            }}>
                                {currentLetter.body_text}
                            </div>

                            {currentLetter.santa_reply && (
                                <div style={{ marginTop: 24 }}>
                                    <h3 style={{ fontSize: '1rem', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
                                        🎅 Santa's Reply
                                        {currentLetter.santa_reply.delivery_status === 'sent' && (
                                            <span style={{
                                                fontSize: '0.75rem',
                                                padding: '2px 8px',
                                                borderRadius: 4,
                                                background: 'var(--green)20',
                                                color: 'var(--green)'
                                            }}>
                                                ✅ Sent
                                            </span>
                                        )}
                                    </h3>
                                    <div style={{
                                        background: 'rgba(200, 50, 50, 0.1)',
                                        padding: 20,
                                        borderRadius: 8,
                                        border: '1px solid var(--red)30',
                                        whiteSpace: 'pre-wrap',
                                        fontFamily: "'Crimson Text', serif",
                                        fontSize: '1.05rem',
                                        lineHeight: 1.6,
                                    }}>
                                        {currentLetter.santa_reply.body_text}
                                    </div>
                                </div>
                            )}

                            {currentLetter.wish_items && currentLetter.wish_items.length > 0 && (
                                <div style={{ marginTop: 24 }}>
                                    <h3 style={{ fontSize: '1rem', marginBottom: 12 }}>
                                        🎁 Wishes from this letter ({currentLetter.wish_items.length})
                                    </h3>
                                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                                        {currentLetter.wish_items.map((item, idx) => (
                                            <span
                                                key={idx}
                                                style={{
                                                    padding: '4px 12px',
                                                    background: 'var(--gold)20',
                                                    color: 'var(--gold)',
                                                    borderRadius: 16,
                                                    fontSize: '0.85rem'
                                                }}
                                            >
                                                {item.normalized_name || item.raw_text}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {currentLetter.moderation_flags && currentLetter.moderation_flags.length > 0 && (
                                <div style={{ marginTop: 24 }}>
                                    <h3 style={{ fontSize: '1rem', marginBottom: 12, color: 'var(--red)' }}>
                                        ⚠️ Moderation Flags
                                    </h3>
                                    {currentLetter.moderation_flags.map((flag, idx) => (
                                        <div
                                            key={idx}
                                            style={{
                                                padding: 12,
                                                background: 'rgba(200, 50, 50, 0.1)',
                                                borderRadius: 8,
                                                marginBottom: 8
                                            }}
                                        >
                                            <strong style={{ color: 'var(--red)' }}>{flag.flag_type}</strong>
                                            {flag.excerpt && (
                                                <div style={{ marginTop: 4, fontSize: '0.9rem', fontStyle: 'italic' }}>
                                                    "{flag.excerpt}"
                                                </div>
                                            )}
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
