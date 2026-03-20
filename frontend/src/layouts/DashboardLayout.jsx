import React, { useState } from 'react';
import { useNavigate, useLocation, Link } from 'react-router-dom';
import {
    LayoutDashboard,
    Upload,
    Video,
    History,
    Settings,
    LogOut,
    Menu,
    X,
    User,
    Bell,
    Search,
    Info,
    LifeBuoy,
    ShieldCheck,
    Mail as MailIcon,
    ChevronDown,
    UserRound,
    Sparkles,
    Users
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import Logo from '../components/common/Logo';

const SidebarItem = ({ icon: Icon, label, path, active, onClick }) => (
    <motion.div
        whileHover={{ x: 4 }}
        whileTap={{ scale: 0.98 }}
    >
        <Link
            to={path}
            onClick={onClick}
            className={`flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-500 group ${active
                ? 'bg-medical-600 text-white shadow-lg shadow-medical-200'
                : 'text-slate-500 dark:text-slate-400 hover:bg-medical-50 dark:hover:bg-medical-500/10 hover:text-medical-600 dark:hover:text-medical-400'
                }`}
        >
            <Icon className={`h-5 w-5 ${active ? 'text-white' : 'text-slate-400 dark:text-slate-500 group-hover:text-medical-600 dark:group-hover:text-medical-400'}`} />
            <span className="font-semibold">{label}</span>
        </Link>
    </motion.div>
);

const DashboardLayout = ({ children }) => {
    const [sidebarOpen, setSidebarOpen] = useState(false);
    const [profileOpen, setProfileOpen] = useState(false);
    const [userName, setUserName] = useState('Admin User');
    const [userRole, setUserRole] = useState('Medical Staff');
    const location = useLocation();
    const navigate = useNavigate();

    const [activePatient, setActivePatient] = useState(null);

    React.useEffect(() => {
        const storedName = localStorage.getItem('medisign_name');
        const storedEmail = localStorage.getItem('medisign_email');
        if (storedName) setUserName(storedName);
        if (storedEmail) setUserRole(storedEmail);

        // Open sidebar by default on desktop
        if (window.innerWidth >= 1024) {
            setSidebarOpen(true);
        }

        const checkPatient = () => {
            const stored = localStorage.getItem('medisign_active_patient');
            if (stored) setActivePatient(JSON.parse(stored));
        };
        checkPatient();
        window.addEventListener('patientChanged', checkPatient);
        return () => window.removeEventListener('patientChanged', checkPatient);
    }, []);

    const menuItems = [
        { icon: LayoutDashboard, label: 'Overview', path: '/dashboard' },
        { icon: Video, label: 'Live Webcam', path: '/dashboard/webcam' },
        { icon: UserRound, label: '3D Interpreter', path: '/dashboard/interpreter' },
        { icon: Sparkles, label: 'Communication Bridge', path: '/dashboard/bridge' },
        { icon: Users, label: 'Patients', path: '/dashboard/patients' },
        { icon: Upload, label: 'Upload Video', path: '/dashboard/upload' },
        { icon: History, label: 'History & Logs', path: '/dashboard/history' },
        { icon: Info, label: 'About MediSign', path: '/dashboard/about' },
        { icon: Settings, label: 'Settings & Support', path: '/dashboard/settings' },
    ];

    const handleLogout = () => {
        localStorage.removeItem('isAuthenticated');
        navigate('/login');
    };

    return (
        <div className="min-h-screen bg-slate-50 dark:bg-slate-950 flex transition-colors duration-500">
            {/* Sidebar */}
            <aside
                className={`fixed inset-y-0 left-0 z-50 w-64 bg-white dark:bg-slate-900 border-r border-slate-200 dark:border-slate-800 transform transition-transform duration-500 ease-in-out lg:relative lg:translate-x-0 ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'
                    }`}
            >
                <div className="h-full flex flex-col p-4">
                    <div className="px-4 mb-8">
                        <Logo size="medium" />
                    </div>

                    <nav className="flex-1 space-y-1">
                        {menuItems.map((item) => (
                            <SidebarItem
                                key={item.path}
                                {...item}
                                active={location.pathname === item.path}
                                onClick={() => window.innerWidth < 1024 && setSidebarOpen(false)}
                            />
                        ))}
                    </nav>

                    <div className="pt-4 border-t border-slate-100 dark:border-slate-800">
                        <button
                            onClick={handleLogout}
                            className="flex items-center space-x-3 w-full px-4 py-3 text-slate-500 dark:text-slate-400 hover:bg-red-50 dark:hover:bg-red-900/20 hover:text-red-600 dark:hover:text-red-400 rounded-xl transition-all duration-500 group"
                        >
                            <LogOut className="h-5 w-5 text-slate-400 group-hover:text-red-600 dark:group-hover:text-red-400" />
                            <span className="font-semibold">Logout</span>
                        </button>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <div className="flex-1 flex flex-col overflow-hidden">
                {/* Header */}
                <header className="h-16 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-4 lg:px-8 transition-colors">
                    <div className="flex items-center lg:hidden">
                        <button
                            onClick={() => setSidebarOpen(true)}
                            className="p-2 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800"
                        >
                            <Menu className="h-6 w-6" />
                        </button>
                    </div>

                    <div className="hidden md:flex items-center bg-slate-100 dark:bg-slate-800 rounded-xl px-3 py-1.5 w-96 border border-slate-200 dark:border-slate-700 focus-within:ring-2 focus-within:ring-medical-500 transition-all">
                        <Search className="h-4 w-4 text-slate-400 mr-2" />
                        <input
                            type="text"
                            placeholder="Search for predictions or logs..."
                            className="bg-transparent border-none focus:outline-none text-sm w-full text-slate-600 dark:text-slate-200 placeholder-slate-400"
                        />
                    </div>

                    <div className="flex items-center space-x-3 lg:space-x-4">
                        {activePatient && (
                            <div className="hidden sm:flex items-center bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-400 px-3 py-1.5 rounded-xl border border-emerald-200 dark:border-emerald-800/50 shadow-sm truncate max-w-[200px]">
                                <span className="h-2 w-2 rounded-full bg-emerald-500 mr-2 animate-pulse"></span>
                                <span className="text-sm font-bold truncate">Patient: {activePatient.name}</span>
                            </div>
                        )}
                        <button className="p-2 text-slate-400 hover:text-medical-600 hover:bg-medical-50 dark:hover:bg-medical-500/10 rounded-lg transition-colors relative">
                            <Bell className="h-5 w-5" />
                            <span className="absolute top-2 right-2 h-2 w-2 bg-red-500 rounded-full border-2 border-white dark:border-slate-900"></span>
                        </button>
                        <div className="h-8 w-px bg-slate-200 dark:bg-slate-800 mx-2"></div>
                        <div className="relative">
                            <div
                                onClick={() => setProfileOpen(!profileOpen)}
                                className="flex items-center space-x-3 cursor-pointer group hover:bg-slate-50 dark:hover:bg-slate-800 p-1.5 rounded-xl transition-all border border-transparent hover:border-slate-100 dark:hover:border-slate-700"
                            >
                                <div className="text-right hidden sm:block">
                                    <p className="text-sm font-bold text-slate-800 dark:text-white leading-none">{userName}</p>
                                    <p className="text-xs font-medium text-slate-500 dark:text-slate-400 mt-1">{userRole}</p>
                                </div>
                                <div className="h-10 w-10 bg-slate-200 dark:bg-slate-800 rounded-full border-2 border-white dark:border-slate-700 shadow-sm flex items-center justify-center text-slate-500 dark:text-slate-400 group-hover:border-medical-500 transition-all relative">
                                    <User className="h-6 w-6" />
                                    <div className="absolute bottom-0 right-0 h-3 w-3 bg-emerald-500 border-2 border-white dark:border-slate-700 rounded-full"></div>
                                </div>
                                <ChevronDown className={`h-4 w-4 text-slate-400 transition-transform ${profileOpen ? 'rotate-180' : ''}`} />
                            </div>

                            {/* Profile Dropdown */}
                            <AnimatePresence>
                                {profileOpen && (
                                    <motion.div
                                        initial={{ opacity: 0, y: 10, scale: 0.95 }}
                                        animate={{ opacity: 1, y: 0, scale: 1 }}
                                        exit={{ opacity: 0, y: 10, scale: 0.95 }}
                                        transition={{ duration: 0.2, ease: "easeOut" }}
                                        className="absolute right-0 mt-2 w-72 bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-100 dark:border-slate-800 py-4 z-[60]"
                                    >
                                        <div className="px-6 py-4 border-b border-slate-50 dark:border-slate-800 mb-2">
                                            <p className="font-black text-slate-800 dark:text-white text-lg leading-none">{userName}</p>
                                            <p className="text-sm text-slate-500 dark:text-slate-400 font-medium mt-1">{userRole}</p>
                                        </div>
                                        <div className="px-2 space-y-1">
                                            <Link to="/dashboard/settings#security-settings" onClick={() => setProfileOpen(false)} className="w-full flex items-center space-x-3 px-4 py-2.5 text-slate-600 dark:text-slate-300 hover:bg-medical-50 dark:hover:bg-medical-500/10 hover:text-medical-600 dark:hover:text-medical-400 rounded-xl transition-all font-semibold text-sm group">
                                                <ShieldCheck className="h-4 w-4 text-slate-400 group-hover:text-medical-600" />
                                                <span>Security Settings</span>
                                            </Link>
                                            <Link to="/dashboard/settings#email-preferences" onClick={() => setProfileOpen(false)} className="w-full flex items-center space-x-3 px-4 py-2.5 text-slate-600 dark:text-slate-300 hover:bg-medical-50 dark:hover:bg-medical-500/10 hover:text-medical-600 dark:hover:text-medical-400 rounded-xl transition-all font-semibold text-sm group">
                                                <MailIcon className="h-4 w-4 text-slate-400 group-hover:text-medical-600" />
                                                <span>Email Preferences</span>
                                            </Link>
                                        </div>
                                        <div className="mt-4 pt-2 border-t border-slate-50 dark:border-slate-800 px-2 text-center">
                                            <p className="text-[10px] font-black text-slate-300 dark:text-slate-600 uppercase tracking-widest mb-2">Workspace: Cardiology Dept</p>
                                            <button
                                                onClick={handleLogout}
                                                className="w-full px-4 py-2.5 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 rounded-xl text-sm font-bold hover:bg-red-100 dark:hover:bg-red-900/30 transition-all flex items-center justify-center space-x-2"
                                            >
                                                <LogOut className="h-4 w-4" />
                                                <span>Sign Out</span>
                                            </button>
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    </div>
                </header>

                {/* Dynamic Page Content */}
                <main className="flex-1 overflow-y-auto p-4 lg:p-8">
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={location.pathname}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            transition={{ duration: 0.3, ease: "easeInOut" }}
                            className="max-w-7xl mx-auto"
                        >
                            {children}
                        </motion.div>
                    </AnimatePresence>
                </main>
            </div>

            {/* Mobile Sidebar Overlay */}
            {sidebarOpen && (
                <div
                    className="fixed inset-0 bg-slate-900/20 dark:bg-black/40 backdrop-blur-sm z-40 lg:hidden"
                    onClick={() => setSidebarOpen(false)}
                />
            )}
        </div>
    );
};

export default DashboardLayout;
