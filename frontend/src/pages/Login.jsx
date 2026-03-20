import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Lock, Mail, Loader2, AlertCircle, Eye, EyeOff } from 'lucide-react';
import AuthLayout from '../layouts/AuthLayout';
import { motion, AnimatePresence } from 'framer-motion';

const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: {
            staggerChildren: 0.1,
            delayChildren: 0.2
        }
    }
};

const itemVariants = {
    hidden: { opacity: 0, y: 15 },
    visible: {
        opacity: 1,
        y: 0,
        transition: { duration: 0.5, ease: "easeOut" }
    }
};

const Login = () => {
    const navigate = useNavigate();
    const [email, setEmail] = useState('admin@medisign.ai');
    const [password, setPassword] = useState('password');
    const [name, setName] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [isSignUp, setIsSignUp] = useState(false);

    // Initialize theme on mount
    React.useEffect(() => {
        const theme = localStorage.getItem('theme') || 'light';
        const root = window.document.documentElement;
        if (theme === 'dark') {
            root.classList.add('dark');
        } else if (theme === 'system') {
            const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
            if (systemTheme === 'dark') root.classList.add('dark');
            else root.classList.remove('dark');
        } else {
            root.classList.remove('dark');
        }
    }, []);

    const handleAuth = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        // Mock auth delay
        setTimeout(() => {
            if (isSignUp) {
                localStorage.setItem('isAuthenticated', 'true');
                localStorage.setItem('medisign_name', name || email.split('@')[0]);
                localStorage.setItem('medisign_email', email);
                navigate('/dashboard');
            } else {
                if (email === 'admin@medisign.ai' && password === 'password') {
                    localStorage.setItem('isAuthenticated', 'true');
                    localStorage.setItem('medisign_name', 'Admin User');
                    localStorage.setItem('medisign_email', email);
                    navigate('/dashboard');
                } else {
                    setError('Invalid credentials. Please try again.');
                }
            }
            setLoading(false);
        }, 1500);
    };

    return (
        <AuthLayout
            title={isSignUp ? "Create an Account" : "Welcome to MediSign"}
            subtitle={isSignUp ? "Join the professional medical workspace" : "Sign in to your professional workspace"}
        >
            <motion.form
                variants={containerVariants}
                initial="hidden"
                animate="visible"
                className="mt-8 space-y-6"
                onSubmit={handleAuth}
            >
                {error && (
                    <motion.div
                        variants={itemVariants}
                        className="bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 p-4 rounded-lg flex items-center text-sm border border-red-100 dark:border-red-900/30"
                    >
                        <AlertCircle className="h-4 w-4 mr-2" />
                        {error}
                    </motion.div>
                )}

                <div className="space-y-4">
                    <AnimatePresence>
                        {isSignUp && (
                            <motion.div 
                                variants={itemVariants}
                                initial={{ opacity: 0, height: 0, overflow: 'hidden' }}
                                animate={{ opacity: 1, height: 'auto', overflow: 'visible' }}
                                exit={{ opacity: 0, height: 0, overflow: 'hidden' }}
                            >
                                <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 ml-1 mb-1">
                                    Full Name
                                </label>
                                <motion.div
                                    whileHover={{ z: 10, scale: 1.01 }}
                                    className="relative group lg:perspective-1000"
                                >
                                    <input
                                        type="text"
                                        value={name}
                                        onChange={(e) => setName(e.target.value)}
                                        className="block w-full px-4 py-3.5 border border-slate-200 dark:border-slate-800 rounded-2xl leading-5 bg-white dark:bg-slate-800 placeholder-slate-400 dark:placeholder-slate-500 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-medical-500 focus:border-transparent sm:text-sm transition-all shadow-sm group-hover:shadow-md"
                                        placeholder="Dr. John Doe"
                                        required={isSignUp}
                                    />
                                </motion.div>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    <motion.div variants={itemVariants}>
                        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 ml-1 mb-1">
                            Email Address / Username
                        </label>
                        <motion.div
                            whileHover={{ z: 10, scale: 1.01 }}
                            className="relative group lg:perspective-1000"
                        >
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400 dark:text-slate-500 group-focus-within:text-medical-600 dark:group-focus-within:text-medical-400">
                                <Mail className="h-5 w-5" />
                            </div>
                            <input
                                type="text"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="block w-full pl-10 pr-3 py-3.5 border border-slate-200 dark:border-slate-800 rounded-2xl leading-5 bg-white dark:bg-slate-800 placeholder-slate-400 dark:placeholder-slate-500 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-medical-500 focus:border-transparent sm:text-sm transition-all shadow-sm group-hover:shadow-md"
                                placeholder="you@example.com"
                                required
                            />
                        </motion.div>
                    </motion.div>

                    <motion.div variants={itemVariants}>
                        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 ml-1 mb-1">
                            Password
                        </label>
                        <motion.div
                            whileHover={{ z: 10, scale: 1.01 }}
                            className="relative group lg:perspective-1000"
                        >
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400 dark:text-slate-500 group-focus-within:text-medical-600 dark:group-focus-within:text-medical-400">
                                <Lock className="h-5 w-5" />
                            </div>
                            <input
                                type={showPassword ? "text" : "password"}
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="block w-full pl-10 pr-12 py-3.5 border border-slate-200 dark:border-slate-800 rounded-2xl leading-5 bg-white dark:bg-slate-800 placeholder-slate-400 dark:placeholder-slate-500 text-slate-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-medical-500 focus:border-transparent sm:text-sm transition-all shadow-sm group-hover:shadow-md"
                                placeholder="••••••••"
                                required
                            />
                            <motion.button
                                whileHover={{ scale: 1.1 }}
                                whileTap={{ scale: 0.9 }}
                                type="button"
                                onClick={() => setShowPassword(!showPassword)}
                                className="absolute inset-y-0 right-0 pr-4 flex items-center text-slate-400 dark:text-slate-500 hover:text-medical-600 dark:hover:text-medical-400 transition-colors"
                            >
                                <AnimatePresence mode="wait">
                                    <motion.div
                                        key={showPassword ? 'eye-off' : 'eye'}
                                        initial={{ opacity: 0, scale: 0.8 }}
                                        animate={{ opacity: 1, scale: 1 }}
                                        exit={{ opacity: 0, scale: 0.8 }}
                                        transition={{ duration: 0.15 }}
                                    >
                                        {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                                    </motion.div>
                                </AnimatePresence>
                            </motion.button>
                        </motion.div>
                    </motion.div>
                </div>

                <motion.div variants={itemVariants} className="flex items-center justify-between">
                    <div className="flex items-center">
                        <input
                            id="remember-me"
                            type="checkbox"
                            className="h-4 w-4 text-medical-600 dark:text-medical-500 focus:ring-medical-500 dark:focus:ring-offset-slate-900 border-slate-300 dark:border-slate-700 dark:bg-slate-800 rounded cursor-pointer"
                        />
                        <label htmlFor="remember-me" className="ml-2 block text-sm text-slate-700 dark:text-slate-300 cursor-pointer">
                            Remember me
                        </label>
                    </div>

                    {!isSignUp && (
                        <div className="text-sm">
                            <a href="#" className="font-semibold text-medical-600 dark:text-medical-400 hover:text-medical-500 dark:hover:text-medical-300 transition-colors">
                                Forgot your password?
                            </a>
                        </div>
                    )}
                </motion.div>

                <motion.div variants={itemVariants}>
                    <motion.button
                        whileHover={{ scale: 1.02, shadow: "0 20px 25px -5px rgb(0 0 0 / 0.1)" }}
                        whileTap={{ scale: 0.98 }}
                        type="submit"
                        disabled={loading}
                        className="group relative w-full flex justify-center py-3.5 px-4 border border-transparent text-sm font-bold rounded-xl text-white bg-gradient-to-r from-medical-600 to-medical-500 hover:from-medical-700 hover:to-medical-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-medical-500 shadow-xl shadow-medical-200/50 dark:shadow-none transition-all disabled:opacity-75 disabled:cursor-not-allowed"
                    >
                        {loading ? (
                            <Loader2 className="h-5 w-5 animate-spin" />
                        ) : (
                            isSignUp ? 'Create Workspace' : 'Sign In to Workspace'
                        )}
                    </motion.button>
                </motion.div>

                <motion.div variants={itemVariants} className="mt-4 text-center">
                    <button
                        type="button"
                        onClick={() => setIsSignUp(!isSignUp)}
                        className="text-sm font-semibold text-medical-600 dark:text-medical-400 hover:text-medical-500 dark:hover:text-medical-300 transition-colors"
                    >
                        {isSignUp ? "Already have an account? Sign In" : "Don't have an account? Create Account"}
                    </button>
                </motion.div>
            </motion.form>
        </AuthLayout>
    );
};

export default Login;
