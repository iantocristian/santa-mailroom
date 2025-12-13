import { useState, useEffect, FormEvent } from 'react';
import { useTranslation } from 'react-i18next';
import { useFamilyStore } from '../store/familyStore';
import { supportedLanguages } from '../i18n';
import type { Family } from '../types';

export default function SettingsPage() {
    const { t, i18n } = useTranslation();
    const { family, fetchFamily, updateFamily, createFamily } = useFamilyStore();
    const [formData, setFormData] = useState({
        name: '',
        language: 'en',
        moderation_strictness: 'medium',
        budget_alert_threshold: '',
        data_retention_years: 5,
        timezone: 'UTC',
    });
    const [isSaving, setIsSaving] = useState(false);
    const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

    useEffect(() => {
        fetchFamily();
    }, [fetchFamily]);

    useEffect(() => {
        if (family) {
            setFormData({
                name: family.name || '',
                language: family.language || 'en',
                moderation_strictness: family.moderation_strictness || 'medium',
                budget_alert_threshold: family.budget_alert_threshold?.toString() || '',
                data_retention_years: family.data_retention_years || 5,
                timezone: family.timezone || 'UTC',
            });
        }
    }, [family]);

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        setIsSaving(true);
        setMessage(null);

        try {
            const updates: Partial<Family> = {
                name: formData.name || undefined,
                language: formData.language,
                moderation_strictness: formData.moderation_strictness,
                budget_alert_threshold: formData.budget_alert_threshold
                    ? parseFloat(formData.budget_alert_threshold) as unknown as number
                    : null,
                data_retention_years: formData.data_retention_years,
                timezone: formData.timezone,
            };

            if (family) {
                await updateFamily(updates);
            } else {
                await createFamily(formData.name);
            }

            setMessage({ type: 'success', text: t('settings.savedSuccess') });
        } catch (err: unknown) {
            const error = err as { response?: { data?: { detail?: string } } };
            setMessage({ type: 'error', text: error.response?.data?.detail || t('settings.saveFailed') });
        } finally {
            setIsSaving(false);
        }
    };

    const handleLanguageChange = (langCode: string) => {
        i18n.changeLanguage(langCode);
    };

    return (
        <div className="page-content">
            <div className="page-header" style={{ marginBottom: 32, padding: 0, border: 'none', background: 'transparent' }}>
                <h1 className="page-title">
                    <span className="title-icon">⚙️</span>
                    {t('settings.title')}
                </h1>
            </div>

            <div style={{ maxWidth: 600 }}>
                <form onSubmit={handleSubmit}>
                    {/* UI Language */}
                    <div className="card" style={{ marginBottom: 24 }}>
                        <div className="card-header">
                            <h2 className="card-title">
                                <span>🌍</span> {t('settings.language')}
                            </h2>
                        </div>
                        <div className="card-body">
                            <div className="form-group">
                                <select
                                    className="form-input"
                                    value={i18n.language}
                                    onChange={(e) => handleLanguageChange(e.target.value)}
                                >
                                    {supportedLanguages.map(lang => (
                                        <option key={lang.code} value={lang.code}>
                                            {lang.native} ({lang.name})
                                        </option>
                                    ))}
                                </select>
                                <small style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                                    {t('settings.languageHint')}
                                </small>
                            </div>
                        </div>
                    </div>

                    {/* Family Info */}
                    <div className="card" style={{ marginBottom: 24 }}>
                        <div className="card-header">
                            <h2 className="card-title">
                                <span>👨‍👩‍👧‍👦</span> {t('settings.familyInfo')}
                            </h2>
                        </div>
                        <div className="card-body">
                            <div className="form-group">
                                <label className="form-label">{t('settings.familyName')}</label>
                                <input
                                    type="text"
                                    className="form-input"
                                    placeholder="The Smith Family"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                />
                            </div>

                            <div className="form-group">
                                <label className="form-label">{t('settings.timezone')}</label>
                                <select
                                    className="form-input"
                                    value={formData.timezone}
                                    onChange={(e) => setFormData({ ...formData, timezone: e.target.value })}
                                >
                                    <option value="UTC">UTC</option>
                                    <option value="America/New_York">Eastern (US)</option>
                                    <option value="America/Chicago">Central (US)</option>
                                    <option value="America/Denver">Mountain (US)</option>
                                    <option value="America/Los_Angeles">Pacific (US)</option>
                                    <option value="Europe/London">London (UK)</option>
                                    <option value="Europe/Paris">Paris (EU)</option>
                                    <option value="Europe/Bucharest">Bucharest (RO)</option>
                                    <option value="Asia/Tokyo">Tokyo (JP)</option>
                                    <option value="Australia/Sydney">Sydney (AU)</option>
                                </select>
                            </div>
                        </div>
                    </div>

                    {/* Budget Settings */}
                    <div className="card" style={{ marginBottom: 24 }}>
                        <div className="card-header">
                            <h2 className="card-title">
                                <span>💰</span> {t('settings.budgetAlerts')}
                            </h2>
                        </div>
                        <div className="card-body">
                            <div className="form-group">
                                <label className="form-label">{t('settings.budgetThreshold')}</label>
                                <input
                                    type="number"
                                    className="form-input"
                                    placeholder="e.g., 500"
                                    value={formData.budget_alert_threshold}
                                    onChange={(e) => setFormData({ ...formData, budget_alert_threshold: e.target.value })}
                                    min="0"
                                    step="0.01"
                                />
                                <small style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                                    {t('settings.budgetThresholdHint')}
                                </small>
                            </div>
                        </div>
                    </div>

                    {/* Content Moderation */}
                    <div className="card" style={{ marginBottom: 24 }}>
                        <div className="card-header">
                            <h2 className="card-title">
                                <span>🛡️</span> {t('settings.contentModeration')}
                            </h2>
                        </div>
                        <div className="card-body">
                            <div className="form-group">
                                <label className="form-label">{t('settings.moderationSensitivity')}</label>
                                <select
                                    className="form-input"
                                    value={formData.moderation_strictness}
                                    onChange={(e) => setFormData({ ...formData, moderation_strictness: e.target.value })}
                                >
                                    <option value="low">{t('settings.moderationLow')}</option>
                                    <option value="medium">{t('settings.moderationMedium')}</option>
                                    <option value="high">{t('settings.moderationHigh')}</option>
                                </select>
                                <small style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                                    {t('settings.moderationHint')}
                                </small>
                            </div>
                        </div>
                    </div>

                    {/* Data & Privacy */}
                    <div className="card" style={{ marginBottom: 24 }}>
                        <div className="card-header">
                            <h2 className="card-title">
                                <span>🔒</span> {t('settings.dataPrivacy')}
                            </h2>
                        </div>
                        <div className="card-body">
                            <div className="form-group">
                                <label className="form-label">{t('settings.dataRetention')}</label>
                                <input
                                    type="number"
                                    className="form-input"
                                    value={formData.data_retention_years}
                                    onChange={(e) => setFormData({ ...formData, data_retention_years: parseInt(e.target.value) || 5 })}
                                    min="1"
                                    max="10"
                                />
                                <small style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                                    {t('settings.dataRetentionHint')}
                                </small>
                            </div>
                        </div>
                    </div>

                    {message && (
                        <div
                            className={`alert-banner ${message.type === 'success' ? 'info' : 'danger'}`}
                            style={{ marginBottom: 24 }}
                        >
                            <span>{message.type === 'success' ? '✅' : '❌'}</span>
                            <span>{message.text}</span>
                        </div>
                    )}

                    <button type="submit" className="btn btn-primary btn-lg" disabled={isSaving}>
                        {isSaving ? t('settings.saving') : `💾 ${t('settings.saveSettings')}`}
                    </button>
                </form>
            </div>
        </div>
    );
}
