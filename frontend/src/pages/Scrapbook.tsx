import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useLettersStore } from '../store/lettersStore';
import { useChildrenStore } from '../store/childrenStore';

export default function ScrapbookPage() {
    const { t } = useTranslation();
    const { letters, isLoading, fetchLetters } = useLettersStore();
    const { children, fetchChildren } = useChildrenStore();
    const [selectedChild, setSelectedChild] = useState<number | undefined>();
    const [expandedLetter, setExpandedLetter] = useState<number | null>(null);

    useEffect(() => {
        fetchChildren();
    }, [fetchChildren]);

    useEffect(() => {
        fetchLetters({ child_id: selectedChild });
    }, [fetchLetters, selectedChild]);

    const getChildName = (childId: number) => {
        return children.find(c => c.id === childId)?.name || 'Unknown';
    };

    const lettersByYear = letters.reduce((acc, letter) => {
        const year = letter.year || new Date(letter.received_at).getFullYear();
        if (!acc[year]) acc[year] = [];
        acc[year].push(letter);
        return acc;
    }, {} as Record<number, typeof letters>);

    const years = Object.keys(lettersByYear)
        .map(Number)
        .sort((a, b) => b - a);

    const formatDate = (dateStr: string) => {
        return new Date(dateStr).toLocaleDateString('en-US', {
            weekday: 'long',
            month: 'long',
            day: 'numeric'
        });
    };

    return (
        <div className="page-content">
            <div className="page-header" style={{ marginBottom: 24, padding: 0, border: 'none', background: 'transparent' }}>
                <h1 className="page-title">
                    <span className="title-icon">📖</span>
                    {t('scrapbook.title')}
                </h1>
            </div>

            {/* Child Filter */}
            <div className="card" style={{ marginBottom: 24 }}>
                <div className="card-body" style={{ padding: '12px 20px' }}>
                    <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                            <label style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{t('scrapbook.child')}</label>
                            <select
                                className="form-input"
                                style={{ width: 'auto', padding: '6px 12px' }}
                                value={selectedChild || ''}
                                onChange={(e) => setSelectedChild(e.target.value ? parseInt(e.target.value) : undefined)}
                            >
                                <option value="">{t('common.allChildren')}</option>
                                {children.map(child => (
                                    <option key={child.id} value={child.id}>{child.name}</option>
                                ))}
                            </select>
                        </div>
                        <div style={{ marginLeft: 'auto', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                            {letters.length} {letters.length !== 1 ? t('common.letters') : t('common.letter')} • {years.length} {years.length !== 1 ? t('common.years') : t('common.year')}
                        </div>
                    </div>
                </div>
            </div>

            {/* Timeline */}
            {isLoading ? (
                <div style={{ textAlign: 'center', padding: 60 }}>
                    <div className="spinner" style={{ margin: '0 auto' }} />
                </div>
            ) : letters.length === 0 ? (
                <div className="card">
                    <div className="card-body">
                        <div className="empty-state">
                            <div className="empty-state-icon">📖</div>
                            <h3>{t('scrapbook.noLettersYet')}</h3>
                            <p>{t('scrapbook.noLettersDesc')}</p>
                        </div>
                    </div>
                </div>
            ) : (
                <div style={{ position: 'relative' }}>
                    <div style={{
                        position: 'absolute',
                        left: 20,
                        top: 0,
                        bottom: 0,
                        width: 2,
                        background: 'linear-gradient(to bottom, var(--gold), var(--red), var(--green))',
                        borderRadius: 2
                    }} />

                    {years.map(year => (
                        <div key={year} style={{ marginBottom: 40 }}>
                            <div style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: 16,
                                marginBottom: 20,
                                position: 'relative'
                            }}>
                                <div style={{
                                    width: 42,
                                    height: 42,
                                    borderRadius: '50%',
                                    background: 'var(--red)',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    fontSize: '1.2rem',
                                    zIndex: 1,
                                    boxShadow: '0 4px 12px rgba(200, 50, 50, 0.3)'
                                }}>
                                    🎄
                                </div>
                                <h2 style={{
                                    margin: 0,
                                    fontSize: '1.5rem',
                                    fontWeight: 700,
                                    color: 'var(--gold)'
                                }}>
                                    {t('scrapbook.christmas', { year })}
                                </h2>
                            </div>

                            <div className="timeline-letters" style={{ marginLeft: 60, display: 'flex', flexDirection: 'column', gap: 16 }}>
                                {lettersByYear[year].map(letter => {
                                    const isExpanded = expandedLetter === letter.id;

                                    return (
                                        <div
                                            key={letter.id}
                                            className="card"
                                            style={{
                                                cursor: 'pointer',
                                                transition: 'transform 0.2s, box-shadow 0.2s',
                                                transform: isExpanded ? 'scale(1.01)' : 'scale(1)',
                                                boxShadow: isExpanded ? '0 8px 24px rgba(0,0,0,0.15)' : undefined
                                            }}
                                            onClick={() => setExpandedLetter(isExpanded ? null : letter.id)}
                                        >
                                            <div className="card-body" style={{ padding: 20 }}>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12 }}>
                                                    <div style={{
                                                        width: 36,
                                                        height: 36,
                                                        borderRadius: '50%',
                                                        background: 'var(--green)20',
                                                        display: 'flex',
                                                        alignItems: 'center',
                                                        justifyContent: 'center',
                                                        fontSize: '1.1rem'
                                                    }}>
                                                        👧
                                                    </div>
                                                    <div>
                                                        <div style={{ fontWeight: 600, fontSize: '1rem' }}>
                                                            {getChildName(letter.child_id)}
                                                        </div>
                                                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                                                            {formatDate(letter.received_at)}
                                                        </div>
                                                    </div>
                                                    <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 12 }}>
                                                        {letter.wish_items && letter.wish_items.length > 0 && (
                                                            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                                                                🎁 {letter.wish_items.length}
                                                            </span>
                                                        )}
                                                        <span style={{ fontSize: '1.5rem' }}>
                                                            {isExpanded ? '📖' : '✉️'}
                                                        </span>
                                                    </div>
                                                </div>

                                                {letter.subject && (
                                                    <div style={{
                                                        fontSize: '1rem',
                                                        fontWeight: 500,
                                                        marginBottom: 8,
                                                        color: 'var(--text-primary)'
                                                    }}>
                                                        "{letter.subject}"
                                                    </div>
                                                )}

                                                {!isExpanded ? (
                                                    <div style={{
                                                        fontSize: '0.9rem',
                                                        color: 'var(--text-secondary)',
                                                        overflow: 'hidden',
                                                        textOverflow: 'ellipsis',
                                                        display: '-webkit-box',
                                                        WebkitLineClamp: 2,
                                                        WebkitBoxOrient: 'vertical'
                                                    }}>
                                                        {letter.body_text}
                                                    </div>
                                                ) : (
                                                    <div style={{ marginTop: 16 }}>
                                                        <div style={{
                                                            background: 'var(--bg-secondary)',
                                                            padding: 20,
                                                            borderRadius: 8,
                                                            whiteSpace: 'pre-wrap',
                                                            fontFamily: "'Crimson Text', serif",
                                                            fontSize: '1.05rem',
                                                            lineHeight: 1.7,
                                                            marginBottom: 20
                                                        }}>
                                                            {letter.body_text}
                                                        </div>

                                                        {letter.santa_reply && (
                                                            <div style={{ marginTop: 16 }}>
                                                                <h4 style={{
                                                                    fontSize: '0.9rem',
                                                                    color: 'var(--text-muted)',
                                                                    marginBottom: 12,
                                                                    display: 'flex',
                                                                    alignItems: 'center',
                                                                    gap: 8
                                                                }}>
                                                                    🎅 {t('scrapbook.santaReply')}
                                                                </h4>
                                                                <div style={{
                                                                    background: 'rgba(200, 50, 50, 0.08)',
                                                                    padding: 20,
                                                                    borderRadius: 8,
                                                                    border: '1px solid rgba(200, 50, 50, 0.2)',
                                                                    whiteSpace: 'pre-wrap',
                                                                    fontFamily: "'Crimson Text', serif",
                                                                    fontSize: '1.05rem',
                                                                    lineHeight: 1.7
                                                                }}>
                                                                    {letter.santa_reply.body_text}
                                                                </div>
                                                            </div>
                                                        )}

                                                        {letter.wish_items && letter.wish_items.length > 0 && (
                                                            <div style={{ marginTop: 16 }}>
                                                                <h4 style={{
                                                                    fontSize: '0.9rem',
                                                                    color: 'var(--text-muted)',
                                                                    marginBottom: 12
                                                                }}>
                                                                    🎁 {t('scrapbook.wishes')}
                                                                </h4>
                                                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
                                                                    {letter.wish_items.map((item, idx) => (
                                                                        <span
                                                                            key={idx}
                                                                            style={{
                                                                                padding: '4px 12px',
                                                                                background: 'var(--gold)15',
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
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
