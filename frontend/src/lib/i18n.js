import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
    en: {
        translation: {
            "welcome": "Welcome to Pharmacy App",
            "role_select": "Select your role to continue"
        }
    },
    hi: {
        translation: {
            "welcome": "फार्मेसी ऐप में आपका स्वागत है",
            "role_select": "जारी रखने के लिए अपनी भूमिका चुनें"
        }
    },
    kn: {
        translation: {
            "welcome": "ಫಾರ್ಮಸಿ ಅಪ್ಲಿಕೇಶನ್‌ಗೆ ಸುಸ್ವಾಗತ",
            "role_select": "ಮುಂದುವರಿಯಲು ನಿಮ್ಮ ಪಾತ್ರವನ್ನು ಆಯ್ಕೆಮಾಡಿ"
        }
    }
};

i18n
    .use(initReactI18next)
    .init({
        resources,
        lng: "en",
        fallbackLng: "en",
        interpolation: {
            escapeValue: false
        }
    });

export default i18n;
