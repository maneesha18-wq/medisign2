import { motion, AnimatePresence } from 'framer-motion';

const SupportChat = ({ onClose }) => {
    const [messages, setMessages] = useState([
        { id: 1, role: 'assistant', content: "Hello! I'm your MediSign AI Assistant. How can I help you with medical sign language translation today?" }
    ]);
    const [input, setInput] = useState('');
    const [isTyping, setIsTyping] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isTyping]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMessage = { id: Date.now(), role: 'user', content: input };
        setMessages(prev => [...prev, userMessage]);
        setInput('');
        setIsTyping(true);

        // Simulated AI Response Logic
        setTimeout(() => {
            let response = "I'm not sure about that. Could you please rephrase or contact our technical support representative?";
            const query = input.toLowerCase();

            if (query.includes('how') && query.includes('work')) {
                response = "MediSign uses deep learning (MobileNet and BiLSTMs) to analyze your hand movements in real-time. We map these movements to a dictionary of medical sign language terms specialized for healthcare settings.";
            } else if (query.includes('sign') || query.includes('vocabulary')) {
                response = "We currently support hundreds of common medical signs, including terms for symptoms, anatomy, and general patient care. You can find the full list in our 'Internal Documentation' section.";
            } else if (query.includes('webcam') || query.includes('camera') || query.includes('accuracy')) {
                response = "For best results, ensure you have good lighting directly on your hands and a neutral background. Keep your hands within the frame shown in the 'Live Webcam' view.";
            } else if (query.includes('upload')) {
                response = "You can upload videos in MP4, MOV, or WEBM format (up to 50MB). Our AI will process the video and provide a frame-by-by analysis of the signs detected.";
            } else if (query.includes('hello') || query.includes('hi')) {
                response = "Hi there! How can I assist you with the MediSign platform today?";
            }

            setMessages(prev => [...prev, { id: Date.now() + 1, role: 'assistant', content: response }]);
            setIsTyping(false);
        }, 1500);
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 100, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 100, scale: 0.9 }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="fixed bottom-6 right-6 w-96 max-w-[calc(100vw-3rem)] h-[600px] max-h-[calc(100vh-6rem)] bg-white dark:bg-slate-900 rounded-3xl shadow-2xl border border-slate-100 dark:border-slate-800 flex flex-col overflow-hidden z-[100]"
        >
            {/* Header */}
            <div className="p-4 bg-medical-600 dark:bg-medical-500 text-white flex items-center justify-between">
                <div className="flex items-center space-x-3">
                    <motion.div
                        initial={{ rotate: -20, scale: 0.8 }}
                        animate={{ rotate: 0, scale: 1 }}
                        transition={{ delay: 0.2 }}
                        className="h-10 w-10 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm"
                    >
                        <Bot className="h-6 w-6 text-white" />
                    </motion.div>
                    <div>
                        <h3 className="font-bold text-sm">MediSign Support AI</h3>
                        <p className="text-[10px] font-medium text-medical-100">Always available to help</p>
                    </div>
                </div>
                <div className="flex items-center space-x-1">
                    <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                        <X className="h-5 w-5" />
                    </button>
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/50 dark:bg-slate-900/50">
                <AnimatePresence>
                    {messages.map((m) => (
                        <motion.div
                            key={m.id}
                            initial={{ opacity: 0, y: 10, scale: 0.95 }}
                            animate={{ opacity: 1, y: 0, scale: 1 }}
                            transition={{ duration: 0.3 }}
                            className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                            <div className={`flex items-start max-w-[85%] space-x-2 ${m.role === 'user' ? 'flex-row-reverse space-x-reverse' : 'flex-row'}`}>
                                <div className={`h-8 w-8 rounded-lg flex items-center justify-center flex-shrink-0 ${m.role === 'user' ? 'bg-medical-100 dark:bg-medical-500/20 text-medical-600' : 'bg-white dark:bg-slate-800 text-slate-500 border border-slate-100 dark:border-slate-800 shadow-sm'}`}>
                                    {m.role === 'user' ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                                </div>
                                <motion.div
                                    layout
                                    className={`p-3 rounded-2xl text-sm font-medium ${m.role === 'user' ? 'bg-medical-600 dark:bg-medical-500 text-white rounded-tr-none' : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-200 border border-slate-100 dark:border-slate-800 shadow-sm rounded-tl-none'}`}
                                >
                                    {m.content}
                                </motion.div>
                            </div>
                        </motion.div>
                    ))}
                </AnimatePresence>
                {isTyping && (
                    <motion.div
                        initial={{ opacity: 0, y: 5 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex justify-start"
                    >
                        <div className="flex items-center space-x-2 bg-white dark:bg-slate-800 p-3 rounded-2xl border border-slate-100 dark:border-slate-800 shadow-sm">
                            <div className="flex space-x-1">
                                <div className="h-1.5 w-1.5 bg-slate-400 rounded-full animate-bounce"></div>
                                <div className="h-1.5 w-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:0.2s]"></div>
                                <div className="h-1.5 w-1.5 bg-slate-400 rounded-full animate-bounce [animation-delay:0.4s]"></div>
                            </div>
                        </div>
                    </motion.div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <form onSubmit={handleSend} className="p-4 bg-white dark:bg-slate-900 border-t border-slate-100 dark:border-slate-800">
                <div className="relative group">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Type your question here..."
                        className="w-full pl-4 pr-12 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-medical-500 text-sm font-medium text-slate-900 dark:text-slate-100 transition-all"
                    />
                    <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        type="submit"
                        disabled={!input.trim() || isTyping}
                        className="absolute right-2 top-1.5 p-1.5 bg-medical-600 dark:bg-medical-500 text-white rounded-lg hover:bg-medical-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
                    >
                        <Send className="h-4 w-4" />
                    </motion.button>
                </div>
            </form>
        </motion.div>
    );
};

export default SupportChat;
