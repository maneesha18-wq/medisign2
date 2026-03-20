import React, { useState } from 'react';
import { Mail, MessageCircle, Phone, FileQuestion, ExternalLink, Bot } from 'lucide-react';
import SupportChat from './SupportChat';

const SupportView = () => {
    const [showChat, setShowChat] = useState(false);

    return (
        <div className="space-y-8 animate-in fade-in duration-500 relative">
            <div>
                <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Help & Support</h1>
                <p className="text-slate-500 dark:text-slate-400 mt-2 font-medium italic">We're here to assist you with any questions or technical issues.</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2 space-y-6">
                    <div className="bg-white dark:bg-slate-900 rounded-3xl p-8 shadow-sm border border-slate-100 dark:border-slate-800 transition-colors">
                        <h3 className="text-xl font-bold text-slate-800 dark:text-white mb-6 flex items-center">
                            <Mail className="h-5 w-5 mr-3 text-medical-600 dark:text-medical-400" />
                            Contact Technical Support
                        </h3>
                        {/* ... rest of the section remains same ... */}
                        <form className="space-y-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-1 ml-1">Full Name</label>
                                    <input type="text" className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-medical-500 transition-all font-medium text-slate-900 dark:text-slate-100" placeholder="Dr. John Doe" />
                                </div>
                                <div>
                                    <label className="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-1 ml-1">Department</label>
                                    <input type="text" className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-medical-500 transition-all font-medium text-slate-900 dark:text-slate-100" placeholder="Cardiology" />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-1 ml-1">Problem Description</label>
                                <textarea rows="4" className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-medical-500 transition-all font-medium text-slate-900 dark:text-slate-100" placeholder="Describe the issue you're facing..."></textarea>
                            </div>
                            <button className="px-8 py-3 bg-medical-600 dark:bg-medical-500 text-white rounded-xl font-bold hover:bg-medical-700 dark:hover:bg-medical-600 transition-all shadow-lg shadow-medical-200 dark:shadow-none">
                                Send Support Request
                            </button>
                        </form>
                    </div>

                    <div className="bg-white dark:bg-slate-900 rounded-3xl p-8 shadow-sm border border-slate-100 dark:border-slate-800 transition-colors">
                        <h3 className="text-xl font-bold text-slate-800 dark:text-white mb-6 flex items-center">
                            <FileQuestion className="h-5 w-5 mr-3 text-medical-600 dark:text-medical-400" />
                            Frequently Asked Questions
                        </h3>
                        <div className="space-y-4">
                            {[
                                { q: "How do I improve webcam recognition accuracy?", a: "Ensure good lighting and keep the camera at eye level. Avoid cluttered backgrounds." },
                                { q: "What video formats are supported for upload?", a: "We support MP4, MOV, and WEBM formats with a maximum file size of 50MB." },
                                { q: "Can I use MediSign on my mobile device?", a: "Yes, our dashboard is fully responsive and works on modern mobile browsers." }
                            ].map((item, i) => (
                                <div key={i} className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-100 dark:border-slate-800">
                                    <h4 className="font-bold text-slate-800 dark:text-slate-200 mb-1">{item.q}</h4>
                                    <p className="text-sm text-slate-500 dark:text-slate-400 font-medium">{item.a}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                <div className="space-y-6">
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

            {showChat && (
                <>
                    <div className="fixed inset-0 bg-slate-900/20 dark:bg-black/40 backdrop-blur-sm z-[90] animate-in fade-in duration-300" onClick={() => setShowChat(false)} />
                    <SupportChat onClose={() => setShowChat(false)} />
                </>
            )}
        </div>
    );
};

export default SupportView;
