import React, { useState, useRef, useEffect } from 'react';
import { 
   Mic, 
   MicOff, 
   Send, 
   Trash2, 
   Download, 
   PlusCircle, 
   Camera,
   RefreshCcw,
   Activity,
   Volume2,
   UserRound
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import SignAvatar from './SignAvatar';

const InterpreterView = () => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [messages, setMessages] = useState([
    { role: 'patient', text: 'Hello doctor, I have pain here', time: '14:02' },
    { role: 'doctor', text: 'How long have you had this?', time: '14:03' },
    { role: 'patient', text: 'About three days now', time: '14:04' }
  ]);
  const [waveformHeights, setWaveformHeights] = useState(new Array(7).fill(4));
  const avatarRef = useRef(null);
  const recognitionRef = useRef(null);
  const feedRef = useRef(null);

  // Auto-scroll feed
  useEffect(() => {
    if (feedRef.current) {
      feedRef.current.scrollTop = feedRef.current.scrollHeight;
    }
  }, [messages]);

  // Waveform animation
  useEffect(() => {
    let interval;
    if (isListening) {
      interval = setInterval(() => {
        setWaveformHeights(prev => prev.map(() => 4 + Math.random() * 18));
      }, 110);
    } else {
      setWaveformHeights(new Array(7).fill(4));
    }
    return () => clearInterval(interval);
  }, [isListening]);

  const toggleMic = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  const startListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Browser doesn't support speech recognition.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => setIsListening(true);
    recognition.onresult = (event) => {
      const current = event.results[0][0].transcript;
      setTranscript(current);
      if (event.results[0].isFinal) {
        handleSendMessage(current);
        stopListening();
      }
    };
    recognition.onerror = () => stopListening();
    recognition.onend = () => setIsListening(false);

    recognitionRef.current = recognition;
    recognition.start();
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsListening(false);
  };

  const handleSendMessage = (text = transcript) => {
    if (!text.trim()) return;
    
    const now = new Date();
    const time = now.getHours().toString().padStart(2, '0') + ':' + now.getMinutes().toString().padStart(2, '0');
    
    setMessages(prev => [...prev, { role: 'doctor', text: text.trim(), time }]);
    setTranscript('');
    
    // Trigger avatar signing
    if (avatarRef.current) {
      avatarRef.current.signSentence(text);
    }
  };

  const handleManualSign = (e) => {
    e.preventDefault();
    handleSendMessage();
  };

  const clearTranscript = () => setTranscript('');

  const saveTranscript = () => {
    const text = messages.map(m => `[${m.time}] ${m.role === 'doctor' ? 'Doctor' : 'Patient'}: ${m.text}`).join('\n');
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `medisign-transcript-${new Date().toISOString().slice(0, 10)}.txt`;
    a.click();
  };

  const addClinicalNote = () => {
    const note = prompt('Enter clinical note:');
    if (note && note.trim()) {
      handleSendMessage(`[Clinical Note] ${note.trim()}`);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Sign Translation Platform</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1 font-medium italic">3D Interpreter & Communication Bridge</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <div className="px-3 py-1.5 bg-emerald-50 dark:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 rounded-full text-xs font-black uppercase tracking-widest flex items-center border border-emerald-100 dark:border-emerald-900/30">
            <div className="h-1.5 w-1.5 bg-emerald-500 rounded-full mr-2 animate-pulse"></div>
            Sign Language Active
          </div>
          <div className="px-3 py-1.5 bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 rounded-full text-xs font-black uppercase tracking-widest flex items-center border border-indigo-100 dark:border-indigo-900/30">
            AI Interpreter
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Panel: Avatar & Mic */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white dark:bg-slate-900 rounded-3xl shadow-sm border border-slate-200 dark:border-slate-800 overflow-hidden flex flex-col min-h-[500px]">
            <div className="px-6 py-4 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between bg-slate-50/50 dark:bg-slate-800/50">
              <span className="text-xs font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest">Doctor → Patient Interpreter</span>
              <div className="flex items-center space-x-2">
                <div className="h-2 w-2 bg-emerald-500 rounded-full"></div>
                <span className="text-[10px] font-bold text-slate-500">Avatar Online</span>
              </div>
            </div>

            <div className="flex-1 flex flex-col items-center justify-center p-6 bg-slate-50/30 dark:bg-slate-950/30">
              <SignAvatar ref={avatarRef} />
            </div>

            <div className="p-6 border-t border-slate-100 dark:border-slate-800 space-y-4">
              <div className="flex flex-col space-y-2">
                <span className="text-[10px] font-black text-slate-400 dark:text-slate-500 uppercase tracking-widest">Live Transcript</span>
                <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-2xl border border-slate-100 dark:border-slate-800/50 min-h-[60px] relative transition-all">
                  <p className="text-slate-800 dark:text-slate-200 font-mono text-sm leading-relaxed italic">
                    {transcript || (isListening ? '...' : 'Speech will appear here...')}
                    {isListening && <span className="inline-block w-2 h-4 bg-emerald-500 ml-1 animate-pulse"></span>}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={toggleMic}
                  className={`flex-shrink-0 h-14 w-14 rounded-full flex items-center justify-center transition-all shadow-lg ${
                    isListening 
                    ? 'bg-rose-500 text-white shadow-rose-200 dark:shadow-none animate-pulse' 
                    : 'bg-white dark:bg-slate-800 text-slate-400 hover:text-emerald-500 border border-slate-200 dark:border-slate-700'
                  }`}
                >
                  {isListening ? <MicOff className="h-6 w-6" /> : <Mic className="h-6 w-6" />}
                </motion.button>

                <div className="flex-1 flex flex-col">
                  <span className="text-sm font-bold text-slate-700 dark:text-slate-300">
                    {isListening ? 'Listening...' : 'Push to speak'}
                  </span>
                  <span className="text-xs text-slate-500 mt-0.5">
                    {isListening ? 'Speak medical terms clearly' : 'Avatar signs automatically'}
                  </span>
                </div>

                <div className="flex items-center gap-1.5 h-6">
                  {waveformHeights.map((h, i) => (
                    <motion.div
                      key={i}
                      animate={{ height: h }}
                      className="w-1 bg-emerald-500 rounded-full transition-all"
                    />
                  ))}
                </div>
              </div>

              <form onSubmit={handleManualSign} className="relative flex items-center">
                <input
                  type="text"
                  value={transcript}
                  onChange={(e) => setTranscript(e.target.value)}
                  placeholder="Type symptoms or instructions manually..."
                  className="w-full bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-5 py-3 pr-12 text-sm focus:ring-2 focus:ring-emerald-500 outline-none transition-all dark:text-white"
                />
                <button 
                  type="submit"
                  className="absolute right-2 p-2 text-slate-400 hover:text-emerald-500 transition-colors"
                >
                  <Send className="h-5 w-5" />
                </button>
              </form>
            </div>
          </div>
        </div>

        {/* Right Panel: Feed & Tools */}
        <div className="space-y-6">
          <div className="bg-white dark:bg-slate-900 rounded-3xl shadow-sm border border-slate-200 dark:border-slate-800 flex flex-col h-[500px]">
            <div className="px-6 py-4 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between">
              <h3 className="text-sm font-black text-slate-800 dark:text-white uppercase tracking-widest flex items-center">
                <Activity className="h-4 w-4 mr-2 text-emerald-500" />
                Live Conversation
              </h3>
              <div className="flex space-x-1">
                <button onClick={() => setMessages([])} className="p-1.5 text-slate-400 hover:text-rose-500 transition-colors" title="Clear chat">
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>

            <div 
              ref={feedRef}
              className="flex-1 overflow-y-auto p-6 space-y-4 bg-slate-50/20 dark:bg-slate-950/20"
            >
              <AnimatePresence>
                {messages.map((msg, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex flex-col ${msg.role === 'doctor' ? 'items-end' : 'items-start'}`}
                  >
                    <div className={`max-w-[85%] px-4 py-3 rounded-2xl text-sm leading-relaxed shadow-sm ${
                      msg.role === 'doctor' 
                      ? 'bg-emerald-600 text-white rounded-tr-none' 
                      : 'bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-200 border border-slate-100 dark:border-slate-700 rounded-tl-none'
                    }`}>
                      {msg.text}
                    </div>
                    <span className="text-[10px] font-bold text-slate-400 dark:text-slate-500 mt-1.5 px-1 uppercase tracking-tighter">
                      {msg.role === 'doctor' ? `You via Avatar · ${msg.time}` : `Patient via SL · ${msg.time}`}
                    </span>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>

            <div className="p-4 border-t border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/50">
               <div className="grid grid-cols-2 gap-3">
                  <button 
                    onClick={saveTranscript}
                    className="flex items-center justify-center space-x-2 py-2.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 rounded-xl text-xs font-bold hover:bg-slate-50 dark:hover:bg-slate-700 transition-all"
                  >
                    <Download className="h-3.5 w-3.5" />
                    <span>Save Log</span>
                  </button>
                  <button 
                    onClick={addClinicalNote}
                    className="flex items-center justify-center space-x-2 py-2.5 bg-emerald-600 text-white rounded-xl text-xs font-bold hover:bg-emerald-700 transition-all shadow-lg shadow-emerald-200 dark:shadow-none"
                  >
                    <PlusCircle className="h-3.5 w-3.5" />
                    <span>Add Note</span>
                  </button>
               </div>
            </div>
          </div>

          <div className="bg-indigo-600 rounded-3xl p-6 text-white shadow-xl relative overflow-hidden group">
            <div className="relative z-10">
              <h4 className="font-black uppercase tracking-widest text-[10px] opacity-80 mb-1">Quick Action</h4>
              <p className="text-lg font-bold leading-snug">Demo medical patterns for patient instruction</p>
              <button 
                onClick={() => handleSendMessage("Take this medicine twice daily, please")}
                className="mt-4 px-4 py-2 bg-white/20 hover:bg-white/30 backdrop-blur-md rounded-xl text-xs font-black uppercase tracking-widest transition-all border border-white/10"
              >
                Trigger Instruction
              </button>
            </div>
            <UserRound className="absolute -bottom-4 -right-4 h-24 w-24 opacity-10 rotate-12 group-hover:scale-110 transition-transform duration-500" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default InterpreterView;
