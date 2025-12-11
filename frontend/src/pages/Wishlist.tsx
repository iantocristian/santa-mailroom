import { useState, useEffect } from 'react';
import { useWishlistStore } from '../store/wishlistStore';
import { useChildrenStore } from '../store/childrenStore';
import { COUNTRIES } from '../constants/countries';

const STATUS_LABELS: Record<string, { label: string; color: string; icon: string }> = {
    pending: { label: 'Pending', color: 'var(--gold)', icon: '⏳' },
    approved: { label: 'Approved', color: 'var(--green)', icon: '✅' },
    denied: { label: 'Denied', color: 'var(--red)', icon: '❌' },
    purchased: { label: 'Purchased', color: 'var(--accent)', icon: '🎁' },
};

export default function WishlistPage() {
    const { items, isLoading, fetchItems, updateItem } = useWishlistStore();
    const { children, fetchChildren } = useChildrenStore();
    const [selectedChild, setSelectedChild] = useState<number | undefined>();
    const [selectedStatus, setSelectedStatus] = useState<string>('');

    useEffect(() => {
        fetchChildren();
    }, [fetchChildren]);

    useEffect(() => {
        fetchItems({ child_id: selectedChild, status: selectedStatus || undefined });
    }, [fetchItems, selectedChild, selectedStatus]);

    const handleStatusChange = async (itemId: number, newStatus: string) => {
        await updateItem(itemId, { status: newStatus });
    };

    const getCountryName = (code?: string | null) => {
        if (!code) return null;
        return COUNTRIES.find(c => c.code === code)?.name || code;
    };

    const totalBudget = items
        .filter(item => item.status === 'approved' || item.status === 'purchased')
        .reduce((sum, item) => sum + (Number(item.estimated_price) || 0), 0);

    return (
        <div className="page-content">
            <div className="page-header" style={{ marginBottom: 24, padding: 0, border: 'none', background: 'transparent' }}>
                <h1 className="page-title">
                    <span className="title-icon">🎁</span>
                    Wishlist
                </h1>
                {totalBudget > 0 && (
                    <div style={{
                        background: 'var(--card-bg)',
                        padding: '8px 16px',
                        borderRadius: 8,
                        border: '1px solid var(--border-secondary)'
                    }}>
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Estimated Budget: </span>
                        <span style={{ color: 'var(--gold)', fontWeight: 600 }}>${totalBudget.toFixed(2)}</span>
                    </div>
                )}
            </div>

            {/* Filters */}
            <div className="card" style={{ marginBottom: 24 }}>
                <div className="card-body" style={{ padding: '12px 20px' }}>
                    <div className="filter-row" style={{ display: 'flex', gap: 16, alignItems: 'center', flexWrap: 'wrap' }}>
                        <div className="filter-item" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
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

                        <div className="filter-item" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                            <label style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Status:</label>
                            <select
                                className="form-input"
                                style={{ width: 'auto', padding: '6px 12px' }}
                                value={selectedStatus}
                                onChange={(e) => setSelectedStatus(e.target.value)}
                            >
                                <option value="">All Statuses</option>
                                <option value="pending">Pending</option>
                                <option value="approved">Approved</option>
                                <option value="denied">Denied</option>
                                <option value="purchased">Purchased</option>
                            </select>
                        </div>

                        <div className="filter-count" style={{ marginLeft: 'auto', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                            {items.length} item{items.length !== 1 ? 's' : ''}
                        </div>
                    </div>
                </div>
            </div>

            {/* Wishlist Items */}
            {isLoading ? (
                <div style={{ textAlign: 'center', padding: 60 }}>
                    <div className="spinner" style={{ margin: '0 auto' }} />
                </div>
            ) : items.length === 0 ? (
                <div className="card">
                    <div className="card-body">
                        <div className="empty-state">
                            <div className="empty-state-icon">🎁</div>
                            <h3>No wishes yet</h3>
                            <p>When children send letters to Santa, their wishes will appear here!</p>
                        </div>
                    </div>
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 16 }}>
                    {items.map(item => {
                        const child = children.find(c => c.id === item.child_id);
                        const statusInfo = STATUS_LABELS[item.status] || STATUS_LABELS.pending;

                        return (
                            <div key={item.id} className="card" style={{ overflow: 'hidden' }}>
                                {item.product_image_url && (
                                    <div style={{
                                        height: 140,
                                        background: 'var(--bg-secondary)',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        overflow: 'hidden'
                                    }}>
                                        <img
                                            src={item.product_image_url}
                                            alt={item.normalized_name || item.raw_text}
                                            style={{ maxWidth: '100%', maxHeight: '100%', objectFit: 'contain' }}
                                        />
                                    </div>
                                )}
                                <div className="card-body">
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                                        <h3 style={{ margin: 0, fontSize: '1rem', fontWeight: 600 }}>
                                            {item.normalized_name || item.raw_text}
                                        </h3>
                                        <span style={{
                                            fontSize: '0.75rem',
                                            padding: '2px 8px',
                                            borderRadius: 4,
                                            background: `${statusInfo.color}20`,
                                            color: statusInfo.color
                                        }}>
                                            {statusInfo.icon} {statusInfo.label}
                                        </span>
                                    </div>

                                    {item.category && (
                                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: 8 }}>
                                            📦 {item.category}
                                        </div>
                                    )}

                                    {child && (
                                        <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: 8 }}>
                                            👧 {child.name} {child.country && `(${getCountryName(child.country)})`}
                                        </div>
                                    )}

                                    {item.estimated_price && (
                                        <div style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--gold)', marginBottom: 12 }}>
                                            {Number(item.estimated_price).toLocaleString('en-US', { style: 'currency', currency: item.currency || 'USD' })}
                                        </div>
                                    )}

                                    <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                                        <select
                                            className="form-input"
                                            style={{ flex: 1, padding: '6px 10px', fontSize: '0.85rem' }}
                                            value={item.status}
                                            onChange={(e) => handleStatusChange(item.id, e.target.value)}
                                        >
                                            <option value="pending">⏳ Pending</option>
                                            <option value="approved">✅ Approved</option>
                                            <option value="denied">❌ Denied</option>
                                            <option value="purchased">🎁 Purchased</option>
                                        </select>

                                        {item.product_url && (
                                            <a
                                                href={item.product_url}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="btn btn-sm btn-secondary"
                                            >
                                                🔗 View
                                            </a>
                                        )}
                                    </div>

                                    {item.status === 'denied' && (
                                        <div style={{ marginTop: 12 }}>
                                            <input
                                                type="text"
                                                className="form-input"
                                                placeholder="Reason for denying..."
                                                style={{ fontSize: '0.85rem', padding: '6px 10px' }}
                                                defaultValue={item.denial_reason || ''}
                                                onBlur={(e) => {
                                                    if (e.target.value !== item.denial_reason) {
                                                        updateItem(item.id, { denial_reason: e.target.value });
                                                    }
                                                }}
                                            />
                                        </div>
                                    )}
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
