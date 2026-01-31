import { Outlet } from 'react-router-dom';
import { Pill, Sun, Moon, Languages } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import i18n from '@/lib/i18n';

export default function Layout() {
    const [isDark, setIsDark] = useState(false);

    useEffect(() => {
        if (isDark) {
            document.documentElement.classList.add('dark');
        } else {
            document.documentElement.classList.remove('dark');
        }
    }, [isDark]);

    const toggleLang = () => {
        const current = i18n.language;
        i18n.changeLanguage(current === 'en' ? 'hi' : 'en');
    };

    return (
        <div className="min-h-screen bg-background font-sans antialiased transition-colors duration-300">
            <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
                <div className="container flex h-14 max-w-screen-2xl items-center px-4">
                    <div className="mr-4 flex items-center space-x-2">
                        <Pill className="h-6 w-6 text-primary" />
                        <span className="font-bold sm:inline-block">PharmaAssist</span>
                    </div>
                    <div className="flex flex-1 items-center justify-end space-x-2">
                        <Button variant="ghost" size="icon" onClick={toggleLang} className="h-9 w-9">
                            <Languages className="h-4 w-4" />
                        </Button>
                        <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => setIsDark(!isDark)}
                            className="h-9 w-9"
                        >
                            {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
                            <span className="sr-only">Toggle theme</span>
                        </Button>
                    </div>
                </div>
            </header>
            <main className="flex-1">
                <Outlet />
            </main>
        </div>
    );
}
