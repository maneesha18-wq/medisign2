import React from 'react';
import { Shield, BookOpen, Users, Globe } from 'lucide-react';

const AboutView = () => {
    return (
        <div className="space-y-8 animate-in fade-in duration-500">
            <div>
                <h1 className="text-3xl font-bold text-slate-900 dark:text-white">About MediSign</h1>
                <p className="text-slate-500 dark:text-slate-400 mt-2 font-medium">Bridging the communication gap in healthcare through AI.</p>
            </div>

            <div className="bg-white dark:bg-slate-900 rounded-3xl p-8 shadow-sm border border-slate-100 dark:border-slate-800 transition-colors">
                <div className="max-w-3xl">
                    <h2 className="text-2xl font-bold text-slate-800 dark:text-white mb-4 text-medical-600 dark:text-medical-400">Our Mission</h2>
                    <p className="text-slate-600 dark:text-slate-300 leading-relaxed mb-6 font-medium">
                        MediSign was founded with a single goal: to ensure that every patient, regardless of their ability to speak or hear, receives the highest quality of medical care. By leveraging state-of-the-art deep learning, we provide real-time translation of medical sign language, empowering healthcare providers and patients to communicate with clarity and confidence.
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="flex items-start space-x-4">
                            <div className="bg-medical-50 dark:bg-medical-500/10 p-3 rounded-xl text-medical-600 dark:text-medical-400">
                                <Shield className="h-6 w-6" />
                            </div>
                            <div>
                                <h4 className="font-bold text-slate-800 dark:text-slate-200">Clinical Accuracy</h4>
                                <p className="text-sm text-slate-500 dark:text-slate-400">Trained on specialized medical sign datasets for high precision.</p>
                            </div>
                        </div>
                        <div className="flex items-start space-x-4">
                            <div className="bg-emerald-50 dark:bg-emerald-500/10 p-3 rounded-xl text-emerald-600 dark:text-emerald-400">
                                <Globe className="h-6 w-6" />
                            </div>
                            <div>
                                <h4 className="font-bold text-slate-800 dark:text-slate-200">Accessibility First</h4>
                                <p className="text-sm text-slate-500 dark:text-slate-400">Designed to be inclusive and easy to use in high-stress environments.</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 gap-8">
                <div className="bg-medical-600 dark:bg-medical-700 rounded-3xl p-8 text-white transition-colors">
                    <h3 className="text-xl font-bold mb-4 flex items-center">
                        <Users className="h-5 w-5 mr-3" />
                        Our Vision
                    </h3>
                    <p className="text-medical-100 dark:text-medical-200 text-sm leading-relaxed mb-6 font-medium">
                        We envision a world where language is no longer a barrier to life-saving medical treatment. We are constantly expanding our vocabulary and improving our models to support more signs and languages.
                    </p>
                    <a
                        href="https://sign1news.com/"
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-block bg-white dark:bg-slate-100 text-medical-600 dark:text-medical-700 px-6 py-2 rounded-xl font-bold hover:bg-medical-50 dark:hover:bg-white transition-colors"
                    >
                        Read Sign Language News
                    </a>
                </div>
            </div>
        </div>
    );
};

export default AboutView;
