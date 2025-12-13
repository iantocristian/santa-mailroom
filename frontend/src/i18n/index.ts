import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

// Import translations
import en from '../locales/en/translation.json';
import ro from '../locales/ro/translation.json';
import de from '../locales/de/translation.json';
import es from '../locales/es/translation.json';
import it from '../locales/it/translation.json';
import fr from '../locales/fr/translation.json';
import pl from '../locales/pl/translation.json';
import hu from '../locales/hu/translation.json';

export const supportedLanguages = [
    { code: 'en', name: 'English', native: 'English' },
    { code: 'ro', name: 'Romanian', native: 'Română' },
    { code: 'de', name: 'German', native: 'Deutsch' },
    { code: 'es', name: 'Spanish', native: 'Español' },
    { code: 'it', name: 'Italian', native: 'Italiano' },
    { code: 'fr', name: 'French', native: 'Français' },
    { code: 'pl', name: 'Polish', native: 'Polski' },
    { code: 'hu', name: 'Hungarian', native: 'Magyar' },
];

i18n
    .use(LanguageDetector)
    .use(initReactI18next)
    .init({
        resources: {
            en: { translation: en },
            ro: { translation: ro },
            de: { translation: de },
            es: { translation: es },
            it: { translation: it },
            fr: { translation: fr },
            pl: { translation: pl },
            hu: { translation: hu },
        },
        fallbackLng: 'en',
        supportedLngs: supportedLanguages.map(l => l.code),
        nonExplicitSupportedLngs: true, // Allow de-DE to match 'de', ro-RO to match 'ro', etc.
        load: 'languageOnly', // Strip region codes: de-DE → de, ro-RO → ro
        interpolation: {
            escapeValue: false, // React already escapes values
        },
        detection: {
            order: ['localStorage', 'navigator'],
            caches: ['localStorage'],
        },
    });

export default i18n;
