import React, { useState, useEffect } from 'react';
import { Settings as SettingsIcon, Shield, Bell, User, Cpu, Volume2, Moon, Sun, Monitor, Info, Lock, LogOut, FileQuestion, Bot, MessageCircle, ExternalLink } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';
import SupportChat from './SupportChat';

const Settings = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const [theme, setTheme] = useState(localStorage.getItem('theme') || 'light');
    const [showChat, setShowChat] = useState(false);

    const handleLogout = () => {
        localStorage.removeItem('isAuthenticated');
        navigate('/login');
    };

    useEffect(() => {
        if (location.hash) {
            const id = location.hash.replace('#', '');
            const element = document.getElementById(id);
            if (element) {
                setTimeout(() => {
                    element.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }, 100);
            }
        }
    }, [location]);

    useEffect(() => {
        localStorage.setItem('theme', theme);
        const root = window.document.documentElement;

        if (theme === 'dark') {
            root.classList.add('dark');
        } else if (theme === 'light') {
            root.classList.remove('dark');
        } else if (theme === 'system') {
            const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
            if (systemTheme === 'dark') {
                root.classList.add('dark');
            } else {
                root.classList.remove('dark');
            }
        }
    }, [theme]);

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-start">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Settings & Support</h1>
                    <p className="text-slate-500 dark:text-slate-400 mt-1 font-medium italic">Manage your workspace preferences, model configuration, and access help</p>
                </div>
                <button
                    onClick={handleLogout}
                    className="flex items-center px-4 py-2 bg-rose-50 dark:bg-rose-900/20 text-rose-600 dark:text-rose-400 rounded-xl font-bold border border-rose-100 dark:border-rose-900/30 hover:bg-rose-100 dark:hover:bg-rose-900/40 transition-colors"
                >
                    <LogOut className="h-4 w-4 mr-2" />
                    Logout
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="md:col-span-2 space-y-6">
                    {/* Theme Preferences */}
                    <div className="bg-white dark:bg-slate-900 rounded-3xl shadow-sm border border-slate-100 dark:border-slate-800 overflow-hidden">
                        <div className="p-8">
                            <h3 className="text-lg font-bold text-slate-800 dark:text-white mb-6 flex items-center">
                                <Monitor className="h-5 w-5 mr-3 text-medical-600 dark:text-medical-400" />
                                Appearance & Theme
                            </h3>
                            <div className="grid grid-cols-3 gap-4">
                                {[
                                    { id: 'light', icon: Sun, label: 'Light' },
                                    { id: 'dark', icon: Moon, label: 'Dark' },
                                    { id: 'system', icon: Monitor, label: 'System' }
                                ].map((t) => (
                                    <button
                                        key={t.id}
                                        onClick={() => setTheme(t.id)}
                                        className={`p-4 rounded-2xl border-2 transition-all flex flex-col items-center gap-2 ${theme === t.id
                                            ? 'border-medical-500 bg-medical-50 dark:bg-medical-500/10 text-medical-600 dark:text-medical-400'
                                            : 'border-slate-100 dark:border-slate-800 hover:border-slate-200 dark:hover:border-slate-700 text-slate-500 dark:text-slate-400'
                                            }`}
                                    >
                                        <t.icon className={`h-6 w-6 ${theme === t.id ? 'text-medical-600 dark:text-medical-400' : 'text-slate-400'}`} />
                                        <span className="text-xs font-bold uppercase tracking-wider">{t.label}</span>
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>

                    <div className="bg-white dark:bg-slate-900 rounded-3xl shadow-sm border border-slate-100 dark:border-slate-800 overflow-hidden">
                        <div className="p-8 border-b border-slate-100 dark:border-slate-800">
                            <h3 className="text-lg font-bold text-slate-800 dark:text-white mb-6 flex items-center">
                                <Cpu className="h-5 w-5 mr-3 text-medical-600 dark:text-medical-400" />
                                Model Configuration
                            </h3>

                            <div className="space-y-6">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="font-bold text-slate-700 dark:text-slate-200">GPU Acceleration</p>
                                        <p className="text-sm text-slate-500 dark:text-slate-400">Enable faster inference using local GPU resources</p>
                                    </div>
                                    <div className="h-6 w-11 bg-medical-600 rounded-full relative cursor-pointer">
                                        <div className="absolute right-1 top-1 h-4 w-4 bg-white rounded-full"></div>
                                    </div>
                                </div>

                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="font-bold text-slate-700 dark:text-slate-200">Confidence Threshold</p>
                                        <p className="text-sm text-slate-500 dark:text-slate-400">Minimum probability required for a positive match</p>
                                    </div>
                                    <div className="w-32">
                                        <input type="range" className="w-full h-1.5 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-medical-600 dark:accent-medical-500" />
                                        <div className="flex justify-between text-[10px] font-bold text-slate-400 dark:text-slate-500 mt-1">
                                            <span>0.0</span>
                                            <span>0.85</span>
                                            <span>1.0</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="p-8">
                            <h3 className="text-lg font-bold text-slate-800 dark:text-white mb-6 flex items-center">
                                <Volume2 className="h-5 w-5 mr-3 text-medical-600 dark:text-medical-400" />
                                Audio & Feedback
                            </h3>

                            <div className="space-y-6">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="font-bold text-slate-700 dark:text-slate-200">Automatic TTS Playback</p>
                                        <p className="text-sm text-slate-500 dark:text-slate-400">Play predicted medical terms immediately after inference</p>
                                    </div>
                                    <div className="h-6 w-11 bg-slate-200 dark:bg-slate-700 rounded-full relative cursor-pointer">
                                        <div className="absolute left-1 top-1 h-4 w-4 bg-white rounded-full"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white dark:bg-slate-900 rounded-3xl shadow-sm border border-slate-100 dark:border-slate-800 overflow-hidden mb-6">
                        <div id="security-settings" className="p-8 border-b border-slate-100 dark:border-slate-800">
                            <h3 className="text-lg font-bold text-slate-800 dark:text-white mb-6 flex items-center">
                                <Shield className="h-5 w-5 mr-3 text-medical-600 dark:text-medical-400" />
                                Security Settings
                            </h3>
                            <div className="space-y-6">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="font-bold text-slate-700 dark:text-slate-200">Two-Factor Authentication (2FA)</p>
                                        <p className="text-sm text-slate-500 dark:text-slate-400">Add an extra layer of security to your account</p>
                                    </div>
                                    <div className="h-6 w-11 bg-medical-600 rounded-full relative cursor-pointer">
                                        <div className="absolute right-1 top-1 h-4 w-4 bg-white rounded-full"></div>
                                    </div>
                                </div>
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="font-bold text-slate-700 dark:text-slate-200">Session Timeout</p>
                                        <p className="text-sm text-slate-500 dark:text-slate-400">Automatically log out after inactivity</p>
                                    </div>
                                    <select className="bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 text-sm rounded-xl focus:ring-medical-500 focus:border-medical-500 block p-2.5">
                                        <option>15 Minutes</option>
                                        <option>30 Minutes</option>
                                        <option>1 Hour</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                        
                        <div id="email-preferences" className="p-8">
                            <h3 className="text-lg font-bold text-slate-800 dark:text-white mb-6 flex items-center">
                                <Bell className="h-5 w-5 mr-3 text-medical-600 dark:text-medical-400" />
                                Email Preferences
                            </h3>
                            <div className="space-y-6">
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="font-bold text-slate-700 dark:text-slate-200">Security Alerts</p>
                                        <p className="text-sm text-slate-500 dark:text-slate-400">Get notified about unusual activity</p>
                                    </div>
                                    <div className="h-6 w-11 bg-medical-600 rounded-full relative cursor-pointer">
                                        <div className="absolute right-1 top-1 h-4 w-4 bg-white rounded-full"></div>
                                    </div>
                                </div>
                                <div className="flex items-center justify-between">
                                    <div>
                                        <p className="font-bold text-slate-700 dark:text-slate-200">Weekly Summary</p>
                                        <p className="text-sm text-slate-500 dark:text-slate-400">Receive a weekly digest of your activity</p>
                                    </div>
                                    <div className="h-6 w-11 bg-slate-200 dark:bg-slate-700 rounded-full relative cursor-pointer">
                                        <div className="absolute left-1 top-1 h-4 w-4 bg-white rounded-full"></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="space-y-6">
                    {/* About Us Card */}
                    <div className="bg-white dark:bg-slate-900 p-8 rounded-3xl border border-slate-100 dark:border-slate-800 shadow-sm">
                        <h3 className="font-bold text-lg mb-4 flex items-center dark:text-white">
                            <Info className="h-5 w-5 mr-3 text-medical-600 dark:text-medical-400" />
                            About MediSign
                        </h3>
                        <p className="text-slate-600 dark:text-slate-400 text-sm mb-4 font-medium leading-relaxed">
                            MediSign is an AI-powered platform designed to facilitate communication between healthcare providers and patients using sign language.
                        </p>
                        <div className="flex items-center text-xs font-bold text-slate-400 dark:text-slate-500">
                            <span>Version 1.2.0-stable</span>
                        </div>
                    </div>

                    {/* AI Support and Internal Docs Moved from SupportView */}
                    <div className="bg-medical-50 dark:bg-medical-500/10 rounded-3xl p-8 border border-medical-100 dark:border-medical-900/30 transition-colors shadow-sm">
                        <h3 className="text-lg font-bold text-slate-800 dark:text-white mb-4 flex items-center">
                            <Bot className="h-5 w-5 mr-2 text-medical-600 dark:text-medical-400" />
                            AI Support Agent
                        </h3>
                        <p className="text-sm text-slate-600 dark:text-slate-400 mb-6 font-medium leading-relaxed">
                            Need immediate answers? Our AI agent is trained to help you with MediSign settings, sign vocabulary, and troubleshooting.
                        </p>
                        <button
                            onClick={() => setShowChat(true)}
                            className="w-full flex items-center justify-center space-x-2 bg-medical-600 dark:bg-medical-500 text-white py-3 rounded-xl font-bold hover:bg-medical-700 dark:hover:bg-medical-600 transition-all shadow-md active:scale-95"
                        >
                            <MessageCircle className="h-5 w-5" />
                            <span>Start AI Chat</span>
                        </button>
                    </div>

                    <div className="bg-slate-900 rounded-3xl p-8 text-white relative overflow-hidden group">
                        <div className="relative z-10">
                            <h3 className="font-bold text-lg mb-4">Internal Documentation</h3>
                            <p className="text-slate-400 text-sm mb-6 font-medium">Access detailed guides on model parameters and integration protocols.</p>
                            <a
                                href={`mailto:${localStorage.getItem('medisign_email') || ''}?subject=Internal%20Documentation`}
                                className="flex items-center space-x-2 text-medical-400 font-bold hover:text-medical-300 transition-colors"
                            >
                                <span>Email Docs</span>
                                <ExternalLink className="h-4 w-4" />
                            </a>
                        </div>
                        <div className="absolute -bottom-10 -right-10 h-32 w-32 bg-medical-500/10 rounded-full blur-2xl group-hover:bg-medical-500/20 transition-all duration-500"></div>
                    </div>

                </div>
            </div>

            {/* AI Chat Modal */}
            {showChat && (
                <>
                    <div className="fixed inset-0 bg-slate-900/20 dark:bg-black/40 backdrop-blur-sm z-[90] animate-in fade-in duration-300" onClick={() => setShowChat(false)} />
                    <SupportChat onClose={() => setShowChat(false)} />
                </>
            )}
        </div>
    );
};

export default Settings;
