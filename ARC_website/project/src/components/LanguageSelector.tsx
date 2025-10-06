import React, { useState, useEffect, useRef } from 'react';

interface Language {
    code: string;
    name: string;
    flag: string;
}

const languages: Language[] = [
    { code: 'en', name: 'English', flag: '🇺🇸' },
    { code: "ro", name: "Română", flag: "🇷🇴" },
    { code: 'es', name: 'Español', flag: '🇪🇸' },
    { code: 'fr', name: 'Français', flag: '🇫🇷' },
    { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
    { code: 'it', name: 'Italiano', flag: '🇮🇹' },
    { code: 'pt', name: 'Português', flag: '🇵🇹' },
];

interface LanguageSelectorProps {
    textColor?: string;
}

const LanguageSelector: React.FC<LanguageSelectorProps> = ({ textColor = "text-gray-900" }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [currentLang, setCurrentLang] = useState<Language>(languages[0]);
    const dropdownRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        // Initialize Google Translate
        if (!(window as any).googleTranslateElementInit) {
            (window as any).googleTranslateElementInit = () => {
                new (window as any).google.translate.TranslateElement({
                    pageLanguage: 'en',
                    includedLanguages: languages.map(lang => lang.code).join(','),
                    layout: (window as any).google.translate.TranslateElement.InlineLayout.SIMPLE,
                    autoDisplay: false
                }, 'google_translate_element_hidden');
            };

            const script = document.createElement('script');
            script.src = '//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
            document.head.appendChild(script);
        }
    }, []);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const translatePage = (langCode: string) => {
        const googleTranslateCombo = document.querySelector('.goog-te-combo') as HTMLSelectElement;
        if (googleTranslateCombo) {
            googleTranslateCombo.value = langCode;
            googleTranslateCombo.dispatchEvent(new Event('change'));
        }

        const selectedLang = languages.find(lang => lang.code === langCode) || languages[0];
        setCurrentLang(selectedLang);
        setIsOpen(false);
    };

    return (
        <div className="relative" ref={dropdownRef}>
            {/* Hidden Google Translate Element */}
            <div id="google_translate_element_hidden" style={{ display: 'none' }}></div>

            {/* Custom Language Selector */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={`flex items-center space-x-2 px-3 py-2 rounded-lg hover:bg-white/20 transition-all duration-200 ${textColor}`}
                aria-label="Select language"
            >
                <span className="text-lg">{currentLang.flag}</span>
                <span className="hidden sm:inline text-sm font-medium">{currentLang.code.toUpperCase()}</span>
                <svg
                    className={`w-4 h-4 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
            </button>

            {/* Dropdown Menu */}
            {isOpen && (
                <div className="absolute top-full mt-2 right-0 w-64 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50 max-h-96 overflow-y-auto">
                    {languages.map((language) => (
                        <button
                            key={language.code}
                            onClick={() => translatePage(language.code)}
                            className={`w-full flex items-center space-x-3 px-4 py-2 text-left hover:bg-gray-100 transition-colors duration-150 ${
                                currentLang.code === language.code ? 'bg-blue-50 text-blue-600' : 'text-gray-700'
                            }`}
                        >
                            <span className="text-lg">{language.flag}</span>
                            <span className="text-sm font-medium">{language.name}</span>
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
};

export default LanguageSelector;