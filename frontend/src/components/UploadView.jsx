import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Upload as UploadIcon,
    File,
    X,
    Loader2,
    CheckCircle2,
    Volume2,
    Play,
    FileVideo
} from 'lucide-react';
import predictionService from '../services/predictionService';
import { motion, AnimatePresence } from 'framer-motion';
import ConfidenceChart from './ConfidenceChart';

const UploadView = () => {
    const navigate = useNavigate();
    const [file, setFile] = useState(null);
    const [processing, setProcessing] = useState(false);
    const [result, setResult] = useState(null);
    const [dragActive, setDragActive] = useState(false);
    const [language, setLanguage] = useState('en');
    const [activePatient, setActivePatient] = useState(null);

    React.useEffect(() => {
        const checkPatient = () => {
            const stored = localStorage.getItem('medisign_active_patient');
            if (stored) {
                const pat = JSON.parse(stored);
                setActivePatient(pat);
                setLanguage(pat.language);
            }
        };
        checkPatient();
        window.addEventListener('patientChanged', checkPatient);
        return () => window.removeEventListener('patientChanged', checkPatient);
    }, []);

    const playSound = (url) => {
        if (!url) return;
        const fullUrl = predictionService.getFullAudioUrl(url);
        const audio = new Audio(fullUrl);
        // Force volume to 1.0 (max)
        audio.volume = 1.0;
        audio.play().catch(e => console.error("Audio playback failed:", e));
    };

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            setFile(e.dataTransfer.files[0]);
        }
    };

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
        }
    };

    const handleProcess = async () => {
        if (!file) return;
        setProcessing(true);
        setResult(null);
        try {
            const data = await predictionService.recognize(file, language);
            setResult(data);
            if (data.audio_url) {
                playSound(data.audio_url);
            }

            // Save to frontend history
            const activePat = JSON.parse(localStorage.getItem('medisign_active_patient'));
            const newHistory = {
                id: Date.now(),
                term: data.prediction,
                confidence: data.confidence,
                time: new Date().toISOString().replace('T', ' ').substring(0, 19),
                source: 'Upload',
                status: 'Success',
                patientId: activePat?.id || null,
                patientName: activePat?.name || 'Guest'
            };
            const existingHistory = JSON.parse(localStorage.getItem('medisign_history') || '[]');
            localStorage.setItem('medisign_history', JSON.stringify([newHistory, ...existingHistory]));

        } catch (err) {
            console.error('Processing failed:', err);
        } finally {
            setProcessing(false);
        }
    };

    // Force play audio when result comes in
    React.useEffect(() => {
        if (result && result.audio_url) {
            const fullUrl = predictionService.getFullAudioUrl(result.audio_url);
            const audioObj = new Audio(fullUrl);
            audioObj.volume = 1.0;
            audioObj.play().catch(e => console.warn("Auto-play blocked by browser:", e));
        }
    }, [result]);

    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Video File Processing</h1>
                    <p className="text-slate-500 dark:text-slate-400 mt-1 font-medium italic">Upload pre-recorded sign language clips for analysis</p>
                </div>
                
                <div className="flex items-center space-x-3 bg-white dark:bg-slate-800 p-2 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700">
                    <label htmlFor="language-select" className="text-sm font-bold text-slate-700 dark:text-slate-300 ml-2">Translation:</label>
                    <select
                        id="language-select"
                        value={language}
                        onChange={(e) => setLanguage(e.target.value)}
                        className="bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-slate-800 dark:text-white text-sm rounded-lg focus:ring-medical-500 focus:border-medical-500 block p-2 outline-none font-medium cursor-pointer"
                    >
                        <option value="en">English (Default)</option>
                        <option value="te">Telugu</option>
                        <option value="hi">Hindi</option>
                        <option value="mr">Marathi</option>
                        <option value="ta">Tamil</option>
                    </select>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2 space-y-6">
                    {!file ? (
                        <motion.div
                            layout
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            onDragEnter={handleDrag}
                            onDragLeave={handleDrag}
                            onDragOver={handleDrag}
                            onDrop={handleDrop}
                            className={`relative h-96 rounded-3xl border-4 border-dashed transition-all flex flex-col items-center justify-center p-12 text-center cursor-pointer overflow-hidden ${dragActive
                                ? 'border-medical-500 bg-medical-50/50 dark:bg-medical-500/10'
                                : 'border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:border-medical-300 dark:hover:border-medical-700 hover:bg-slate-50 dark:hover:bg-slate-800/50'
                                }`}
                        >
                            <motion.div
                                whileHover={{ scale: 1.1, rotate: 5 }}
                                className="h-24 w-24 bg-medical-50 dark:bg-medical-500/10 rounded-full flex items-center justify-center mb-6 text-medical-600 dark:text-medical-400 shadow-sm"
                            >
                                <UploadIcon className="h-10 w-10" />
                            </motion.div>
                            <div>
                                <h3 className="text-xl font-bold text-slate-800 dark:text-white">Drag and drop video files</h3>
                                <p className="text-slate-500 dark:text-slate-400 mt-2 font-medium">MP4, MOV, or WEBM formats supported</p>
                            </div>

                            <motion.label
                                whileHover={{ scale: 1.05 }}
                                whileTap={{ scale: 0.95 }}
                                className="mt-8 px-6 py-3 bg-medical-600 dark:bg-medical-500 text-white rounded-xl font-bold shadow-lg shadow-medical-100 dark:shadow-none cursor-pointer hover:bg-medical-700 dark:hover:bg-medical-600 transition-all"
                            >
                                Browse Files
                                <input type="file" className="hidden" accept="video/*" onChange={handleFileChange} />
                            </motion.label>

                            <AnimatePresence>
                                {dragActive && (
                                    <motion.div
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        exit={{ opacity: 0 }}
                                        className="absolute inset-0 bg-medical-500/10 backdrop-blur-[2px] pointer-events-none flex items-center justify-center"
                                    >
                                        <motion.div
                                            initial={{ scale: 0.8 }}
                                            animate={{ scale: 1 }}
                                            className="bg-white dark:bg-slate-800 px-6 py-3 rounded-2xl shadow-xl font-bold text-medical-600 dark:text-medical-400 border border-medical-200 dark:border-medical-800"
                                        >
                                            <motion.div
                                                animate={{ y: [0, -5, 0] }}
                                                transition={{ repeat: Infinity, duration: 1 }}
                                            >
                                                Drop to upload
                                            </motion.div>
                                        </motion.div>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </motion.div>
                    ) : (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                            className="bg-white dark:bg-slate-900 rounded-3xl shadow-sm border border-slate-100 dark:border-slate-800 overflow-hidden transition-colors"
                        >
                            <div className="p-8 border-b border-slate-50 dark:border-slate-800 flex items-center justify-between">
                                <div className="flex items-center space-x-4">
                                    <motion.div
                                        initial={{ rotate: -10 }}
                                        animate={{ rotate: 0 }}
                                        className="h-16 w-16 bg-medical-50 dark:bg-medical-500/10 rounded-2xl flex items-center justify-center text-medical-600 dark:text-medical-400"
                                    >
                                        <FileVideo className="h-8 w-8" />
                                    </motion.div>
                                    <div>
                                        <h3 className="font-bold text-slate-800 dark:text-white text-lg">{file.name}</h3>
                                        <p className="text-sm text-slate-500 dark:text-slate-400 font-medium">{(file.size / (1024 * 1024)).toFixed(2)} MB • Video File</p>
                                    </div>
                                </div>
                                {!processing && (
                                    <motion.button
                                        whileHover={{ scale: 1.1, color: "#ef4444" }}
                                        onClick={() => { setFile(null); setResult(null); }}
                                        className="p-2 text-slate-400 dark:text-slate-500 hover:bg-red-50 dark:hover:bg-red-500/10 rounded-xl transition-all"
                                    >
                                        <X className="h-6 w-6" />
                                    </motion.button>
                                )}
                            </div>

                            <div className="p-8 bg-slate-50/50 dark:bg-slate-800/30 flex flex-col items-center justify-center min-h-[300px]">
                                <AnimatePresence mode="wait">
                                    {processing ? (
                                        <motion.div
                                            key="processing"
                                            initial={{ opacity: 0, y: 10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            exit={{ opacity: 0, y: -10 }}
                                            className="flex flex-col items-center text-center w-full"
                                        >
                                            <div className="relative h-24 w-24 mb-6">
                                                <div className="absolute inset-0 border-4 border-slate-200 dark:border-slate-700 rounded-full"></div>
                                                <motion.div
                                                    animate={{ rotate: 360 }}
                                                    transition={{ repeat: Infinity, duration: 1, ease: "linear" }}
                                                    className="absolute inset-0 border-4 border-medical-500 rounded-full border-t-transparent"
                                                ></motion.div>
                                                <div className="absolute inset-0 flex items-center justify-center">
                                                    <span className="text-xl font-black text-medical-600 dark:text-medical-400 italic">MS</span>
                                                </div>
                                            </div>
                                            <h3 className="text-xl font-bold text-slate-800 dark:text-white tracking-tight">AI Analysis in Progress</h3>
                                            <p className="text-slate-500 dark:text-slate-400 mt-2 font-medium">Extracting spatial features and sequencing...</p>

                                            <div className="w-64 bg-slate-200 dark:bg-slate-700 h-2 rounded-full mt-6 overflow-hidden">
                                                <motion.div
                                                    initial={{ width: 0 }}
                                                    animate={{ width: "100%" }}
                                                    transition={{ duration: 2, repeat: Infinity }}
                                                    className="h-full bg-medical-600 dark:bg-medical-500 rounded-full"
                                                ></motion.div>
                                            </div>
                                        </motion.div>
                                    ) : result ? (
                                        <motion.div
                                            key="result"
                                            initial={{ opacity: 0, scale: 0.9 }}
                                            animate={{ opacity: 1, scale: 1 }}
                                            className="flex flex-col items-center text-center"
                                        >
                                            <motion.div
                                                initial={{ scale: 0 }}
                                                animate={{ scale: 1 }}
                                                transition={{ type: "spring", damping: 12 }}
                                                className="h-20 w-20 bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 rounded-full flex items-center justify-center mb-6 shadow-sm"
                                            >
                                                <CheckCircle2 className="h-10 w-10" />
                                            </motion.div>
                                            <h3 className="text-2xl font-black text-slate-800 dark:text-white">Processing Complete</h3>
                                            <p className="text-slate-500 dark:text-slate-400 mt-2 font-medium mb-8">Click 'Process New' or clear the file to run another analysis.</p>
                                            <div className="flex space-x-4">
                                                <motion.button
                                                    whileHover={{ scale: 1.05 }}
                                                    whileTap={{ scale: 0.95 }}
                                                    onClick={() => setFile(null)}
                                                    className="px-8 py-3 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-200 rounded-xl font-bold hover:bg-slate-300 dark:hover:bg-slate-600 transition-all"
                                                >
                                                    Clear File
                                                </motion.button>
                                                <motion.button
                                                    whileHover={{ scale: 1.05 }}
                                                    whileTap={{ scale: 0.95 }}
                                                    onClick={() => navigate('/dashboard/history')}
                                                    className="px-8 py-3 bg-medical-50 dark:bg-medical-500/10 text-medical-600 dark:text-medical-400 rounded-xl font-bold border border-medical-100 dark:border-medical-900/30"
                                                >
                                                    Review Data
                                                </motion.button>
                                            </div>
                                        </motion.div>
                                    ) : (
                                        <motion.button
                                            key="empty"
                                            initial={{ opacity: 0 }}
                                            animate={{ opacity: 1 }}
                                            whileHover={{ scale: 1.05 }}
                                            whileTap={{ scale: 0.95 }}
                                            onClick={handleProcess}
                                            className="group relative px-12 py-5 bg-medical-600 dark:bg-medical-500 text-white rounded-2xl font-black text-xl shadow-2xl shadow-medical-200 dark:shadow-none hover:bg-medical-700 dark:hover:bg-medical-600 transition-all flex items-center"
                                        >
                                            <Play className="h-6 w-6 mr-3 fill-white" />
                                            Run AI Analysis
                                        </motion.button>
                                    )}
                                </AnimatePresence>
                            </div>
                        </motion.div>
                    )}
                </div>

                <div className="space-y-6">
                    <div className="bg-white dark:bg-slate-900 p-6 rounded-3xl shadow-sm border border-slate-100 dark:border-slate-800 min-h-[400px] transition-colors">
                        <h3 className="text-lg font-bold text-slate-800 dark:text-white mb-6 flex items-center">
                            <Activity className="h-5 w-5 mr-3 text-medical-600 dark:text-medical-400" />
                            Upload Summary
                        </h3>

                        <AnimatePresence mode="wait">
                            {result ? (
                                <motion.div
                                    key="result"
                                    initial={{ opacity: 0, x: 20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, x: 20 }}
                                    className="space-y-6"
                                >
                                    <div className="bg-medical-50 dark:bg-medical-500/10 p-6 rounded-2xl text-center border border-medical-100 dark:border-medical-900/30">
                                        <p className="text-xs font-black text-medical-800/60 dark:text-medical-400/60 uppercase tracking-widest mb-1">Detected Sign</p>
                                        <h2 className="text-4xl font-black text-medical-700 dark:text-medical-400 tracking-tight">{result.prediction}</h2>
                                        {result.translation && result.translation !== result.prediction && (
                                            <p className="text-2xl font-bold text-medical-500 dark:text-medical-300 mt-2">{result.translation}</p>
                                        )}
                                    </div>

                                    <div className="space-y-2 px-2">
                                        <div className="flex justify-between items-end">
                                            <span className="text-sm font-bold text-slate-700 dark:text-slate-300">Confidence</span>
                                            <span className="text-lg font-black text-slate-900 dark:text-white">{(result.confidence * 100).toFixed(1)}%</span>
                                        </div>
                                        <div className="w-full bg-slate-100 dark:bg-slate-800 h-3 rounded-full overflow-hidden">
                                            <motion.div
                                                initial={{ width: 0 }}
                                                animate={{ width: `${result.confidence * 100}%` }}
                                                transition={{ duration: 1, ease: "easeOut" }}
                                                className="h-full bg-medical-600 dark:bg-medical-500"
                                            ></motion.div>
                                        </div>
                                    </div>

                                    <div className="grid grid-cols-2 gap-4">
                                        <motion.div
                                            initial={{ opacity: 0, y: 10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: 0.2 }}
                                            className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-slate-100 dark:border-slate-800/50"
                                        >
                                            <p className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest leading-none mb-2">Class Index</p>
                                            <p className="text-xl font-bold text-slate-800 dark:text-slate-200">#42</p>
                                        </motion.div>
                                        <motion.div
                                            initial={{ opacity: 0, y: 10 }}
                                            animate={{ opacity: 1, y: 0 }}
                                            transition={{ delay: 0.3 }}
                                            className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-slate-100 dark:border-slate-800/50"
                                        >
                                            <p className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest leading-none mb-2">Frames</p>
                                            <p className="text-xl font-bold text-slate-800 dark:text-slate-200">60</p>
                                        </motion.div>
                                    </div>

                                    {result.audio_url && (
                                        <div className="w-full mt-4 flex flex-col items-center bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl border border-slate-100 dark:border-slate-800/50">
                                            <div className="flex items-center text-sm font-bold text-slate-700 dark:text-slate-300 mb-3 w-full">
                                                <Volume2 className="h-4 w-4 mr-2" />
                                                Audio Feedback
                                            </div>
                                            <audio 
                                                controls 
                                                autoPlay 
                                                className="w-full h-10 rounded shadow-sm" 
                                                src={predictionService.getFullAudioUrl(result.audio_url)}
                                            >
                                                Your browser does not support the audio element.
                                            </audio>
                                        </div>
                                    )}

                                    {result.all_predictions && Object.keys(result.all_predictions).length > 0 && (
                                        <div className="pt-4 border-t border-slate-100 dark:border-slate-800">
                                            <ConfidenceChart
                                                predictions={result.all_predictions}
                                                topLabel={result.prediction}
                                            />
                                        </div>
                                    )}
                                </motion.div>
                            ) : (
                                <motion.div
                                    key="empty"
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    className="flex flex-col items-center justify-center py-24 text-center"
                                >
                                    <File className="h-16 w-16 text-slate-100 dark:text-slate-800 mb-4" />
                                    <p className="text-slate-400 dark:text-slate-500 font-medium px-4">Upload a video to see processing metrics and prediction results.</p>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                </div>
            </div>
        </div>
    );
};

const Activity = ({ className }) => (
    <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
    </svg>
);

export default UploadView;
