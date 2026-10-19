import i18n from 'i18next'
import {initReactI18next} from 'react-i18next'
import LanguageDetector from 'i18next-browser-languagedetector';
import en from './en.json'
import sl from './sl.json'

export const LANGUAGES = ['sl', 'en'] as const

i18n
    .use(LanguageDetector)
    .use(initReactI18next)
    .init({
        resources: {sl: {translation: sl}, en: {translation: en}},
        fallbackLng: 'sl',
        interpolation: {escapeValue: false},
    })

i18n.on('languageChanged', (lang) => { document.documentElement.lang = lang })
document.documentElement.lang = i18n.language
export default i18n
