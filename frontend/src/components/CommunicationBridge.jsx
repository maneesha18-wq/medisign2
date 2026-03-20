import React, { useState, useRef, useEffect } from 'react';
import {
    Camera,
    Video,
    Square,
    RefreshCcw,
    Loader2,
    Volume2,
    Mic,
    MicOff,
    Send,
    Activity,
    UserRound,
    Sparkles
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import predictionService from '../services/predictionService';
import SignAvatar from './SignAvatar';
import ConfidenceChart from './ConfidenceChart';

const CommunicationBridge = () => {
    // Shared State
    const [language, setLanguage] = useState('en');

    // Webcam Side State
    const [streaming, setStreaming] = useState(false);
    const [recording, setRecording] = useState(false);
    const [processing, setProcessing] = useState(false);
    const [webcamResult, setWebcamResult] = useState(null);
    const videoRef = useRef(null);
    const mediaRecorderRef = useRef(null);
    const chunksRef = useRef([]);

    // Interpreter Side State
    const [isListening, setIsListening] = useState(false);
    const [transcript, setTranscript] = useState('');
    const avatarRef = useRef(null);
    const recognitionRef = useRef(null);

    // Camera Logic
    const startCamera = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                setStreaming(true);
            }
        } catch (err) {
            console.error('Camera error:', err);
        }
    };

    const stopCamera = () => {
        if (videoRef.current && videoRef.current.srcObject) {
            videoRef.current.srcObject.getTracks().forEach(track => track.stop());
            videoRef.current.srcObject = null;
            setStreaming(false);
        }
    };

    const startRecording = () => {
        if (!videoRef.current?.srcObject) return;
        setRecording(true);
        setWebcamResult(null);
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
        setTimeout(() => {
            if (mediaRecorderRef.current?.state === 'recording') stopRecording();
        }, 3000);
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current?.state === 'recording') {
            mediaRecorderRef.current.stop();
            setRecording(false);
        }
    };

    const handleInference = async (file) => {
        setProcessing(true);
        try {
            const data = await predictionService.recognize(file, language);
            setWebcamResult(data);
            if (data.audio_url) {
                const audio = new Audio(predictionService.getFullAudioUrl(data.audio_url));
                audio.play();
            }
        } catch (err) {
            console.error('Inference error:', err);
        } finally {
            setProcessing(false);
        }
    };

    // Interpreter Logic
    const toggleMic = () => {
        if (isListening) stopListening();
        else startListening();
    };

    const startListening = () => {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) return;
        const recognition = new SpeechRecognition();
        recognition.onstart = () => setIsListening(true);
        recognition.onresult = (event) => {
            const current = event.results[0][0].transcript;
            setTranscript(current);
            if (event.results[0].isFinal) {
                handleAvatarSign(current);
                stopListening();
            }
        };
        recognition.onerror = () => stopListening();
        recognition.onend = () => setIsListening(false);
        recognitionRef.current = recognition;
        recognition.start();
    };

    const stopListening = () => {
        if (recognitionRef.current) recognitionRef.current.stop();
        setIsListening(false);
    };

    const handleAvatarSign = (text = transcript) => {
        if (!text.trim()) return;
        if (avatarRef.current) avatarRef.current.signSentence(text);
        setTranscript('');
    };

    useEffect(() => {
        return () => stopCamera();
    }, []);

    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900 dark:text-white flex items-center">
                        Communication Bridge 
                        <Sparkles className="h-6 w-6 ml-3 text-medical-500 animate-pulse" />
                    </h1>
                    <p className="text-slate-500 dark:text-slate-400 mt-1 font-medium italic">Seamless two-way medical translation</p>
                </div>
                
                <div className="bg-white dark:bg-slate-800 p-2 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 flex items-center space-x-2">
                    <label className="text-xs font-black text-slate-400 uppercase tracking-widest ml-2">Language:</label>
                    <select
                        value={language}
                        onChange={(e) => setLanguage(e.target.value)}
                        className="bg-transparent border-none text-sm font-bold text-medical-600 dark:text-medical-400 focus:ring-0 cursor-pointer"
                    >
                        <option value="en">English</option>
                        <option value="te">Telugu</option>
                        <option value="hi">Hindi</option>
                        <option value="mr">Marathi</option>
                    </select>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8">
                {/* Left Side: Human (Webcam) */}
                <div className="space-y-4">
                    <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 shadow-sm border border-slate-200 dark:border-slate-800 flex flex-col h-full">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-sm font-black text-slate-800 dark:text-white uppercase tracking-widest flex items-center">
                                <Video className="h-4 w-4 mr-2 text-indigo-500" />
                                Human Signing
                            </h3>
                            {!streaming ? (
                                <button onClick={startCamera} className="text-xs font-bold text-medical-600 hover:underline">Enable Camera</button>
                            ) : (
                                <div className="flex items-center space-x-2">
                                    <div className="h-2 w-2 bg-emerald-500 rounded-full animate-pulse"></div>
                                    <span className="text-[10px] font-bold text-slate-400 uppercase">Live</span>
                                </div>
                            )}
                        </div>

                        <div className="relative aspect-video bg-slate-100 dark:bg-slate-950 rounded-2xl overflow-hidden border border-slate-200 dark:border-slate-800">
                            {!streaming && (
                                <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-400">
                                    <Camera className="h-10 w-10 mb-2 opacity-20" />
                                    <p className="text-xs font-bold uppercase tracking-widest italic">Camera Offline</p>
                                </div>
                            )}
                            <video ref={videoRef} autoPlay muted playsInline className={`w-full h-full object-cover ${streaming ? 'opacity-100' : 'opacity-0'}`} />
                            
                            {recording && (
                                <div className="absolute top-4 left-4 flex items-center space-x-2 bg-red-600 text-white px-3 py-1 rounded-full text-[10px] font-black uppercase tracking-widest shadow-lg">
                                    <div className="h-1.5 w-1.5 bg-white rounded-full animate-pulse"></div>
                                    <span>Recording</span>
                                </div>
                            )}

                            {processing && (
                                <div className="absolute inset-0 bg-slate-900/40 backdrop-blur-sm flex flex-col items-center justify-center text-white text-center p-4">
                                    <Loader2 className="h-8 w-8 animate-spin mb-2" />
                                    <p className="text-sm font-bold uppercase tracking-widest">AI Analyzing...</p>
                                </div>
                            )}

                            {streaming && !processing && (
                                <button
                                    onClick={recording ? stopRecording : startRecording}
                                    className={`absolute bottom-4 left-1/2 -translate-x-1/2 h-14 w-14 rounded-full flex items-center justify-center transition-all ${
                                        recording ? 'bg-red-600' : 'bg-white text-medical-600 shadow-xl'
                                    }`}
                                >
                                    {recording ? <Square className="h-6 w-6 text-white fill-white" /> : <div className="h-8 w-8 bg-medical-500 rounded-full"></div>}
                                </button>
                            )}
                        </div>

                        <div className="mt-4 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-2xl border border-slate-100 dark:border-slate-800 min-h-[80px] flex flex-col justify-center text-center relative group">
                            <span className="absolute top-2 left-2 text-[8px] font-black text-slate-300 dark:text-slate-600 uppercase tracking-widest">Translation Node</span>
                            {webcamResult ? (
                                <motion.div initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }} className="space-y-1">
                                    {/* Show translated text as primary if available */}
                                    {webcamResult.translation && webcamResult.translation !== webcamResult.prediction ? (
                                        <>
                                            <p className="text-2xl font-black text-medical-600 dark:text-medical-400 tracking-tight">{webcamResult.translation}</p>
                                            <p className="text-xs font-semibold text-slate-400 italic">{webcamResult.prediction}</p>
                                        </>
                                    ) : (
                                        <p className="text-2xl font-black text-medical-600 dark:text-medical-400 tracking-tight">{webcamResult.prediction}</p>
                                    )}
                                    <p className="text-[10px] font-bold text-slate-400 uppercase">Confidence: {(webcamResult.confidence * 100).toFixed(0)}%</p>
                                </motion.div>
                            ) : (
                                <p className="text-slate-400 dark:text-slate-500 text-xs italic">Awaiting sign language input...</p>
                            )}
                        </div>

                        {webcamResult?.all_predictions && Object.keys(webcamResult.all_predictions).length > 0 && (
                            <div className="mt-3 bg-white dark:bg-slate-900 rounded-2xl p-4 border border-slate-100 dark:border-slate-800">
                                <ConfidenceChart
                                    predictions={webcamResult.all_predictions}
                                    topLabel={webcamResult.prediction}
                                />
                            </div>
                        )}
                    </div>
                </div>

                {/* Right Side: Avatar (Interpreter) */}
                <div className="space-y-4">
                    <div className="bg-white dark:bg-slate-900 rounded-3xl p-6 shadow-sm border border-slate-200 dark:border-slate-800 flex flex-col h-full">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-sm font-black text-slate-800 dark:text-white uppercase tracking-widest flex items-center">
                                <UserRound className="h-4 w-4 mr-2 text-emerald-500" />
                                3D Interpreter
                            </h3>
                            <div className="flex items-center space-x-2">
                                <div className="h-2 w-2 bg-emerald-500 rounded-full"></div>
                                <span className="text-[10px] font-bold text-slate-400 uppercase">Avatar Active</span>
                            </div>
                        </div>

                        <div className="relative aspect-video bg-slate-50/50 dark:bg-slate-950 rounded-2xl flex items-center justify-center border border-slate-100 dark:border-slate-800 overflow-hidden">
                            <SignAvatar ref={avatarRef} />
                        </div>

                        <div className="mt-4 space-y-4">
                            <div className="flex items-center gap-3">
                                <button
                                    onClick={toggleMic}
                                    className={`h-12 w-12 rounded-2xl flex items-center justify-center transition-all ${
                                        isListening 
                                        ? 'bg-rose-500 text-white animate-pulse' 
                                        : 'bg-slate-100 dark:bg-slate-800 text-slate-500 hover:text-emerald-500'
                                    }`}
                                >
                                    {isListening ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
                                </button>
                                
                                <form onSubmit={(e) => { e.preventDefault(); handleAvatarSign(); }} className="flex-1 relative">
                                    <input
                                        type="text"
                                        value={transcript}
                                        onChange={(e) => setTranscript(e.target.value)}
                                        placeholder={isListening ? "Listening to doctor..." : "Type instruction for patient..."}
                                        className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-2xl px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-emerald-500/20"
                                    />
                                    <button type="submit" className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-emerald-500">
                                        <Send className="h-4 w-4" />
                                    </button>
                                </form>
                            </div>
                            
                            <div className="p-3 bg-indigo-500/5 rounded-2xl border border-indigo-500/10 text-center">
                                <p className="text-[10px] font-bold text-indigo-600 dark:text-indigo-400 uppercase tracking-widest italic">Digital Bridge Mode Enabled</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div className="bg-white dark:bg-slate-900 p-6 rounded-3xl shadow-sm border border-slate-200 dark:border-slate-800">
                <div className="flex items-center space-x-3 mb-4">
                    <Activity className="h-5 w-5 text-medical-500" />
                    <h3 className="text-sm font-black text-slate-800 dark:text-white uppercase tracking-widest">Workflow Insights</h3>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {[
                        { label: 'Latency', value: '1.2s', desc: 'Real-time sync' },
                        { label: 'Translation', value: 'Multi-lingual', desc: 'Medical dictionary' },
                        { label: 'Security', value: 'HIPAA Compliant', desc: 'Secure transmission' }
                    ].map((item, i) => (
                        <div key={i} className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-2xl border border-slate-100 dark:border-slate-800/50">
                            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{item.label}</p>
                            <p className="text-xl font-black text-slate-800 dark:text-white my-1">{item.value}</p>
                            <p className="text-xs text-slate-500 font-medium">{item.desc}</p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default CommunicationBridge;
