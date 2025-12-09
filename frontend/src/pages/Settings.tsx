import { useState, useEffect, FormEvent } from 'react';
import { useFamilyStore } from '../store/familyStore';
import type { Family } from '../types';

export default function SettingsPage() {
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

            setMessage({ type: 'success', text: 'Settings saved successfully!' });
        } catch (err: unknown) {
            const error = err as { response?: { data?: { detail?: string } } };
            setMessage({ type: 'error', text: error.response?.data?.detail || 'Failed to save settings' });
        } finally {
            setIsSaving(false);
        }
    };

    return (
        <div className="page-content">
            <div className="page-header" style={{ marginBottom: 32, padding: 0, border: 'none', background: 'transparent' }}>
                <h1 className="page-title">
                    <span className="title-icon">⚙️</span>
                    Settings
                </h1>
            </div>

            <div style={{ maxWidth: 600 }}>
                <form onSubmit={handleSubmit}>
                    {/* Family Info */}
                    <div className="card" style={{ marginBottom: 24 }}>
                        <div className="card-header">
                            <h2 className="card-title">
                                <span>👨‍👩‍👧‍👦</span> Family Information
                            </h2>
                        </div>
                        <div className="card-body">
                            <div className="form-group">
                                <label className="form-label">Family Name</label>
                                <input
                                    type="text"
                                    className="form-input"
                                    placeholder="The Smith Family"
                                    value={formData.name}
                                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                                />
                            </div>

                            <div className="form-group">
                                <label className="form-label">Timezone</label>
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
                                <span>💰</span> Budget Alerts
                            </h2>
                        </div>
                        <div className="card-body">
                            <div className="form-group">
                                <label className="form-label">Budget Alert Threshold ($)</label>
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
                                    You'll be notified when the total wishlist exceeds this amount. Leave empty to disable.
                                </small>
                            </div>
                        </div>
                    </div>

                    {/* Content Moderation */}
                    <div className="card" style={{ marginBottom: 24 }}>
                        <div className="card-header">
                            <h2 className="card-title">
                                <span>🛡️</span> Content Moderation
                            </h2>
                        </div>
                        <div className="card-body">
                            <div className="form-group">
                                <label className="form-label">Moderation Sensitivity</label>
                                <select
                                    className="form-input"
                                    value={formData.moderation_strictness}
                                    onChange={(e) => setFormData({ ...formData, moderation_strictness: e.target.value })}
                                >
                                    <option value="low">Low - Only flag serious concerns</option>
                                    <option value="medium">Medium - Flag concerning content (Recommended)</option>
                                    <option value="high">High - Flag anything that might indicate struggles</option>
                                </select>
                                <small style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                                    Controls how sensitive the AI is when detecting concerning content in letters.
                                </small>
                            </div>
                        </div>
                    </div>

                    {/* Data & Privacy */}
                    <div className="card" style={{ marginBottom: 24 }}>
                        <div className="card-header">
                            <h2 className="card-title">
                                <span>🔒</span> Data & Privacy
                            </h2>
                        </div>
                        <div className="card-body">
                            <div className="form-group">
                                <label className="form-label">Data Retention (Years)</label>
                                <input
                                    type="number"
                                    className="form-input"
                                    value={formData.data_retention_years}
                                    onChange={(e) => setFormData({ ...formData, data_retention_years: parseInt(e.target.value) || 5 })}
                                    min="1"
                                    max="10"
                                />
                                <small style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                                    How long to keep letters and wishes. Older data will be automatically deleted.
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
                        {isSaving ? 'Saving...' : '💾 Save Settings'}
                    </button>
                </form>
            </div>
        </div>
    );
}
