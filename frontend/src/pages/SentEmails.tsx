import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useChildrenStore } from '../store/childrenStore';
import api from '../api/client';

interface SentEmail {
    id: number;
    child_id: number;
    child_name: string;
    email_type: string;
    subject: string | null;
    body_text: string;
    letter_id: number | null;
    deed_id: number | null;
    sent_at: string;
    delivery_status: string;
}

export default function SentEmailsPage() {
    const { t } = useTranslation();
    const { children, fetchChildren } = useChildrenStore();
    const [emails, setEmails] = useState<SentEmail[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [selectedChild, setSelectedChild] = useState<number | undefined>();
    const [selectedType, setSelectedType] = useState<string | undefined>();
    const [expandedEmail, setExpandedEmail] = useState<number | null>(null);

    const EMAIL_TYPE_LABELS: Record<string, { label: string; icon: string; color: string }> = {
        letter_reply: { label: t('sentEmails.letterReply'), icon: '✉️', color: 'var(--green)' },
        deed_suggestion: { label: t('sentEmails.deedSuggestion'), icon: '⭐', color: 'var(--gold)' },
        deed_congrats: { label: t('sentEmails.deedCongrats'), icon: '🎉', color: 'var(--red)' },
    };

    useEffect(() => {
        fetchChildren();
    }, [fetchChildren]);

    useEffect(() => {
        fetchEmails();
    }, [selectedChild, selectedType]);

    const fetchEmails = async () => {
        setIsLoading(true);
        try {
            const params = new URLSearchParams();
            if (selectedChild) params.append('child_id', selectedChild.toString());
            if (selectedType) params.append('email_type', selectedType);

            const response = await api.get<SentEmail[]>(`/sent-emails?${params.toString()}`);
            setEmails(response.data);
        } finally {
            setIsLoading(false);
        }
    };

    const formatDate = (dateStr: string) => {
        return new Date(dateStr).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    return (
        <div className="page-content">
            <div className="page-header" style={{ marginBottom: 24, padding: 0, border: 'none', background: 'transparent' }}>
                <h1 className="page-title">
                    <span className="title-icon">📤</span>
                    {t('sentEmails.title')}
                </h1>
            </div>

            {/* Filters */}
            <div className="card" style={{ marginBottom: 24 }}>
                <div className="card-body" style={{ padding: '12px 20px' }}>
                    <div className="filter-row" style={{ display: 'flex', gap: 16, alignItems: 'center', flexWrap: 'wrap' }}>
                        <div className="filter-item" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                            <label style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{t('sentEmails.child')}</label>
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

                        <div className="filter-item" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                            <label style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{t('sentEmails.type')}</label>
                            <select
                                className="form-input"
                                style={{ width: 'auto', padding: '6px 12px' }}
                                value={selectedType || ''}
                                onChange={(e) => setSelectedType(e.target.value || undefined)}
                            >
                                <option value="">{t('sentEmails.allTypes')}</option>
                                <option value="letter_reply">{t('sentEmails.letterReplies')}</option>
                                <option value="deed_suggestion">{t('sentEmails.deedSuggestions')}</option>
                                <option value="deed_congrats">{t('sentEmails.congratulations')}</option>
                            </select>
                        </div>

                        <div className="filter-count" style={{ marginLeft: 'auto', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                            {emails.length} email{emails.length !== 1 ? 's' : ''}
                        </div>
                    </div>
                </div>
            </div>

            {/* Email List */}
            {isLoading ? (
                <div style={{ textAlign: 'center', padding: 60 }}>
                    <div className="spinner" style={{ margin: '0 auto' }} />
                </div>
            ) : emails.length === 0 ? (
                <div className="card">
                    <div className="card-body">
                        <div className="empty-state">
                            <div className="empty-state-icon">📤</div>
                            <h3>{t('sentEmails.noEmailsYet')}</h3>
                            <p>{t('sentEmails.noEmailsDesc')}</p>
                        </div>
                    </div>
                </div>
            ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                    {emails.map(email => {
                        const typeInfo = EMAIL_TYPE_LABELS[email.email_type] || { label: email.email_type, icon: '📧', color: 'var(--text-muted)' };
                        const isExpanded = expandedEmail === email.id;

                        return (
                            <div
                                key={email.id}
                                className="card"
                                style={{ cursor: 'pointer' }}
                                onClick={() => setExpandedEmail(isExpanded ? null : email.id)}
                            >
                                <div className="card-body" style={{ padding: '16px 20px' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                                        <div style={{
                                            width: 40,
                                            height: 40,
                                            borderRadius: '50%',
                                            background: `${typeInfo.color}20`,
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            fontSize: '1.2rem',
                                            flexShrink: 0
                                        }}>
                                            {typeInfo.icon}
                                        </div>
                                        <div style={{ flex: 1, minWidth: 0 }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
                                                <span style={{ fontWeight: 600 }}>{email.subject || t('sentEmails.noSubject')}</span>
                                                <span style={{
                                                    fontSize: '0.75rem',
                                                    padding: '2px 8px',
                                                    borderRadius: 10,
                                                    background: `${typeInfo.color}20`,
                                                    color: typeInfo.color
                                                }}>
                                                    {typeInfo.label}
                                                </span>
                                            </div>
                                            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                                                {t('sentEmails.to')} {email.child_name} • {formatDate(email.sent_at)}
                                            </div>
                                        </div>
                                        <div style={{ fontSize: '1.2rem' }}>
                                            {isExpanded ? '📖' : '📨'}
                                        </div>
                                    </div>

                                    {isExpanded && (
                                        <div style={{ marginTop: 16 }}>
                                            <div style={{
                                                background: 'var(--bg-secondary)',
                                                padding: 20,
                                                borderRadius: 8,
                                                whiteSpace: 'pre-wrap',
                                                fontFamily: "'Crimson Text', serif",
                                                fontSize: '1.05rem',
                                                lineHeight: 1.7
                                            }}>
                                                {email.body_text}
                                            </div>

                                            <div style={{ marginTop: 12, fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                                                {t('sentEmails.status')} {email.delivery_status === 'sent' ? `✅ ${t('sentEmails.delivered')}` : `❌ ${t('sentEmails.failed')}`}
                                                {email.letter_id && ` • ${t('sentEmails.relatedToLetter', { id: email.letter_id })}`}
                                                {email.deed_id && ` • ${t('sentEmails.relatedToDeed', { id: email.deed_id })}`}
                                            </div>
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
