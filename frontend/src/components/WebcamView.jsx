import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Camera,
    Video,
    Square,
    RefreshCcw,
    CheckCircle2,
    Loader2,
    Volume2,
    AlertTriangle
} from 'lucide-react';
import predictionService from '../services/predictionService';
import { motion, AnimatePresence } from 'framer-motion';
import ConfidenceChart from './ConfidenceChart';

const WebcamView = () => {
    const navigate = useNavigate();
    const [streaming, setStreaming] = useState(false);
    const [recording, setRecording] = useState(false);
    const [processing, setProcessing] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [countdown, setCountdown] = useState(0);
    const [language, setLanguage] = useState('en');
    const [activePatient, setActivePatient] = useState(null);

    useEffect(() => {
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

    const videoRef = useRef(null);
    const mediaRecorderRef = useRef(null);
    const chunksRef = useRef([]);
    const playSound = (url) => {
        if (!url) return;
        const fullUrl = predictionService.getFullAudioUrl(url);
        const audio = new Audio(fullUrl);
        // Force volume to 1.0 (max)
        audio.volume = 1.0;
        audio.play().catch(e => console.error("Audio playback failed:", e));
    };

    const startCamera = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                setStreaming(true);
                setError(null);
            }
        } catch (err) {
            console.error('Camera error:', err);
            setError('Could not access camera. Please check permissions.');
        }
    };

    const stopCamera = () => {
        if (videoRef.current && videoRef.current.srcObject) {
            const tracks = videoRef.current.srcObject.getTracks();
            tracks.forEach(track => track.stop());
            videoRef.current.srcObject = null;
            setStreaming(false);
        }
    };

    const startRecording = () => {
        if (!videoRef.current?.srcObject) return;

        setRecording(true);
        setResult(null);
        chunksRef.current = [];

        const recorder = new MediaRecorder(videoRef.current.srcObject);
        recorder.ondataavailable = (e) => {
            if (e.data.size > 0) chunksRef.current.push(e.data);
        };

        recorder.onstop = async () => {
            const blob = new Blob(chunksRef.current, { type: 'video/mp4' });
            const file = new File([blob], 'capture.mp4', { type: 'video/mp4' });
            handleInference(file);
        };

        mediaRecorderRef.current = recorder;
        recorder.start();

        // Auto-stop after 3 seconds (project requirement for 60 frames approx)
        setTimeout(() => {
            if (mediaRecorderRef.current?.state === 'recording') {
                stopRecording();
            }
        }, 3000);
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
            mediaRecorderRef.current.stop();
            setRecording(false);
        }
    };

    const handleInference = async (file) => {
        setProcessing(true);
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
                source: 'Webcam',
                status: 'Success',
                patientId: activePat?.id || null,
                patientName: activePat?.name || 'Guest'
            };
            const existingHistory = JSON.parse(localStorage.getItem('medisign_history') || '[]');
            localStorage.setItem('medisign_history', JSON.stringify([newHistory, ...existingHistory]));

        } catch (err) {
            setError('Inference failed. Please try again.');
        } finally {
            setProcessing(false);
        }
    };

    useEffect(() => {
        return () => stopCamera();
    }, []);

    // Force play audio when result comes in
    useEffect(() => {
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
                    <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Live Webcam Capture</h1>
                    <p className="text-slate-500 dark:text-slate-400 mt-1 font-medium italic">Record sign language for real-time translation</p>
                </div>
                
                <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2 bg-white dark:bg-slate-800 p-2 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700">
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

                    {!streaming ? (
                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={startCamera}
                            className="flex items-center space-x-2 px-6 py-3 bg-medical-600 dark:bg-medical-500 text-white rounded-xl font-bold hover:bg-medical-700 dark:hover:bg-medical-600 transition-all shadow-lg shadow-medical-200 dark:shadow-none"
                        >
                            <Camera className="h-5 w-5" />
                            <span>Enable Camera</span>
                        </motion.button>
                    ) : (
                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={stopCamera}
                            className="flex items-center space-x-2 px-6 py-3 bg-slate-200 dark:bg-slate-800 text-slate-700 dark:text-slate-200 rounded-xl font-bold hover:bg-slate-300 dark:hover:bg-slate-700 transition-all"
                        >
                            <RefreshCcw className="h-5 w-5" />
                            <span>Switch Source</span>
                        </motion.button>
                    )}
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2 relative aspect-video bg-slate-900 rounded-3xl overflow-hidden shadow-2xl border-4 border-white dark:border-slate-800 transition-colors">
                    {!streaming && !error && (
                        <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-400">
                            <Camera className="h-16 w-16 mb-4 opacity-20" />
                            <p className="font-semibold text-lg">Camera is currently disabled</p>
                        </div>
                    )}

                    {error && (
                        <div className="absolute inset-0 flex flex-col items-center justify-center text-red-500 bg-red-50/50 dark:bg-red-950/50 backdrop-blur-sm">
                            <AlertTriangle className="h-16 w-16 mb-4" />
                            <p className="font-bold text-lg">{error}</p>
                            <button onClick={startCamera} className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg font-bold">Try Again</button>
                        </div>
                    )}

                    <video
                        ref={videoRef}
                        autoPlay
                        muted
                        playsInline
                        className={`w-full h-full object-cover ${streaming ? 'opacity-100' : 'opacity-0'} transition-opacity`}
                    />

                    {recording && (
                        <motion.div
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            className="absolute top-6 left-6 flex items-center space-x-2 bg-red-600 text-white px-3 py-1.5 rounded-full shadow-lg ring-4 ring-red-500/20"
                        >
                            <motion.div
                                animate={{ opacity: [1, 0.5, 1] }}
                                transition={{ repeat: Infinity, duration: 1 }}
                                className="h-2 w-2 bg-white rounded-full"
                            ></motion.div>
                            <span className="text-xs font-black uppercase tracking-widest">Recording</span>
                        </motion.div>
                    )}

                    {processing && (
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="absolute inset-0 bg-slate-900/60 dark:bg-black/60 backdrop-blur-sm flex flex-col items-center justify-center text-white"
                        >
                            <Loader2 className="h-12 w-12 animate-spin mb-4" />
                            <p className="text-xl font-bold tracking-tight">AI Engine Processing...</p>
                            <p className="text-slate-300 text-sm mt-1">Analyzing 60 frames @ 224x224</p>
                        </motion.div>
                    )}

                    <div className="absolute bottom-8 left-1/2 -translate-x-1/2">
                        {streaming && !processing && (
                            <motion.button
                                whileHover={{ scale: 1.1 }}
                                whileTap={{ scale: 0.9 }}
                                onClick={recording ? stopRecording : startRecording}
                                className={`h-20 w-20 rounded-full border-4 border-white dark:border-slate-700 flex items-center justify-center transition-all ${recording ? 'bg-red-600 hover:bg-red-700' : 'bg-white dark:bg-slate-200 hover:bg-slate-50'
                                    } shadow-2xl`}
                            >
                                {recording ? <Square className="h-8 w-8 text-white fill-white" /> : <div className="h-12 w-12 bg-medical-600 dark:bg-medical-500 rounded-full"></div>}
                            </motion.button>
                        )}
                    </div>
                </div>

                <div className="space-y-6">
                    <div className="bg-white dark:bg-slate-900 p-6 rounded-3xl shadow-sm border border-slate-100 dark:border-slate-800 h-full transition-colors">
                        <h3 className="text-lg font-bold text-slate-800 dark:text-white mb-6 flex items-center">
                            <Video className="h-5 w-5 mr-3 text-medical-600 dark:text-medical-400" />
                            Analysis Results
                        </h3>

                        <AnimatePresence mode="wait">
                            {result && !processing && (
                                <motion.div
                                    key="result"
                                    initial={{ opacity: 0, scale: 0.95 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    exit={{ opacity: 0, scale: 0.95 }}
                                    className="space-y-8"
                                >
                                    <div className="text-center">
                                        <p className="text-xs font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest mb-1">Predicted Sign</p>
                                        <h2 className="text-4xl font-black text-medical-600 dark:text-medical-400 tracking-tight">{result.prediction}</h2>
                                        <motion.button
                                            whileHover={{ scale: 1.05 }}
                                            whileTap={{ scale: 0.95 }}
                                            onClick={() => navigate('/dashboard/history')}
                                            className="mt-4 px-6 py-2 bg-medical-50 dark:bg-medical-500/10 text-medical-600 dark:text-medical-400 rounded-xl font-bold border border-medical-100 dark:border-medical-900/30 text-sm"
                                        >
                                            Review Data
                                        </motion.button>
                                        {result.translation && result.translation !== result.prediction && (
                                            <p className="text-2xl font-bold text-medical-500 dark:text-medical-300 mt-2">{result.translation}</p>
                                        )}
                                    </div>

                                    <div className="space-y-2">
                                        <div className="flex justify-between items-end">
                                            <span className="text-sm font-bold text-slate-700 dark:text-slate-300">Confidence Score</span>
                                            <span className="text-lg font-black text-slate-900 dark:text-white">{(result.confidence * 100).toFixed(1)}%</span>
                                        </div>
                                        <div className="w-full bg-slate-100 dark:bg-slate-800 h-4 rounded-full overflow-hidden border border-slate-200 dark:border-slate-700">
                                            <motion.div
                                                initial={{ width: 0 }}
                                                animate={{ width: `${result.confidence * 100}%` }}
                                                transition={{ duration: 1, ease: "easeOut" }}
                                                className="h-full bg-medical-600 dark:bg-medical-500 rounded-full"
                                            ></motion.div>
                                        </div>
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

                                    <div className="pt-6 border-t border-slate-100 dark:border-slate-800">
                                        <ConfidenceChart
                                            predictions={result.all_predictions}
                                            topLabel={result.prediction}
                                        />
                                    </div>

                                    <button
                                        onClick={() => setResult(null)}
                                        className="w-full py-3 text-slate-500 dark:text-slate-400 font-bold hover:text-medical-600 dark:hover:text-medical-400 transition-colors"
                                    >
                                        Clear Results
                                    </button>
                                </motion.div>
                            )}

                            {!result && !processing && (
                                <motion.div
                                    key="empty"
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    className="flex flex-col items-center justify-center py-12 text-center"
                                >
                                    <div className="h-24 w-24 bg-slate-50 dark:bg-slate-800/50 rounded-full flex items-center justify-center mb-4 border-2 border-dashed border-slate-200 dark:border-slate-700">
                                        <Activity className="h-10 w-10 text-slate-300 dark:text-slate-600" />
                                    </div>
                                    <p className="text-slate-400 dark:text-slate-500 font-medium px-4">Record a sign language clip to see instant AI predictions here.</p>
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

export default WebcamView;
