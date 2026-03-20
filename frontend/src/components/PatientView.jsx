import React, { useState, useEffect, useMemo } from 'react';
import { 
    Users, Plus, X, User, Calendar, Activity, 
    Globe, ShieldCheck, Search, ChevronRight,
    ChevronLeft
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const containerVariants = {
    visible: { 
        opacity: 1, 
        transition: { staggerChildren: 0.05 } 
    }
};

const itemVariants = {
    visible: { 
        opacity: 1, 
        transition: { duration: 0.2 } 
    }
};

const ITEMS_PER_PAGE = 6;

const PatientView = () => {
    const [patients, setPatients] = useState([]);
    const [activePatientId, setActivePatientId] = useState(null);
    const [isMenuOpen, setIsMenuOpen] = useState(false);
    const [searchQuery, setSearchQuery] = useState('');
    const [debouncedSearch, setDebouncedSearch] = useState('');
    const [currentPage, setCurrentPage] = useState(1);

    const [form, setForm] = useState({
        name: '',
        language: 'en',
        disability: 'Deaf'
    });

    useEffect(() => {
        // Load patients
        const localPatients = JSON.parse(localStorage.getItem('medisign_patients') || '[]');
        if (localPatients.length === 0) {
            // Seed default mock
            const seed = [
                { id: 'p1', name: 'John Doe', language: 'en', disability: 'Deaf', totalSessions: 12, lastSession: '2026-03-15' },
                { id: 'p2', name: 'Maria Garcia', language: 'te', disability: 'Both', totalSessions: 4, lastSession: '2026-03-18' }
            ];
            localStorage.setItem('medisign_patients', JSON.stringify(seed));
            setPatients(seed);
        } else {
            setPatients(localPatients);
        }

        // Load active patient
        const active = JSON.parse(localStorage.getItem('medisign_active_patient'));
        if (active) {
            setActivePatientId(active.id);
        }
    }, []);

    // Debounce search
    useEffect(() => {
        const timer = setTimeout(() => {
            setDebouncedSearch(searchQuery);
            setCurrentPage(1); // Reset to page 1 on search
        }, 300);
        return () => clearTimeout(timer);
    }, [searchQuery]);

    const handleCreate = (e) => {
        e.preventDefault();
        const newPatient = {
            id: 'p' + Date.now(),
            name: form.name,
            language: form.language,
            disability: form.disability,
            totalSessions: 0,
            lastSession: 'Never'
        };
        const updatedList = [...patients, newPatient];
        setPatients(updatedList);
        localStorage.setItem('medisign_patients', JSON.stringify(updatedList));
        setIsMenuOpen(false);
        setForm({ name: '', language: 'en', disability: 'Deaf' });
    };

    const handleSetActive = (patient) => {
        setActivePatientId(patient.id);
        localStorage.setItem('medisign_active_patient', JSON.stringify(patient));
        window.dispatchEvent(new Event('patientChanged'));
    };

    const filteredPatients = useMemo(() => {
        return patients.filter(p => p.name.toLowerCase().includes(debouncedSearch.toLowerCase()));
    }, [patients, debouncedSearch]);

    const paginatedPatients = useMemo(() => {
        const start = (currentPage - 1) * ITEMS_PER_PAGE;
        return filteredPatients.slice(start, start + ITEMS_PER_PAGE);
    }, [filteredPatients, currentPage]);

    const totalPages = Math.ceil(filteredPatients.length / ITEMS_PER_PAGE);

    const langMap = {
        'en': 'English',
        'te': 'Telugu',
        'hi': 'Hindi',
        'mr': 'Marathi',
        'ta': 'Tamil'
    };

    return (
        <motion.div variants={containerVariants} animate="visible" className="space-y-8">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <motion.div variants={itemVariants}>
                    <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Patient Directory</h1>
                    <p className="text-slate-500 dark:text-slate-400 mt-2 font-medium">Manage clinical profiles and translation preferences</p>
                </motion.div>
                <motion.div variants={itemVariants} className="flex gap-4">
                    <div className="relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
                        <input
                            type="text"
                            placeholder="Search patients..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="pl-10 pr-4 py-2.5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-medical-500 text-slate-800 dark:text-white"
                        />
                    </div>
                    <button
                        onClick={() => setIsMenuOpen(true)}
                        className="flex items-center space-x-2 px-5 py-2.5 bg-medical-600 dark:bg-medical-500 text-white rounded-xl font-bold hover:bg-medical-700 dark:hover:bg-medical-600 transition-all shadow-lg shadow-medical-200 dark:shadow-none"
                    >
                        <Plus className="h-5 w-5" />
                        <span>New Patient</span>
                    </button>
                </motion.div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {paginatedPatients.map(patient => (
                    <motion.div
                        key={patient.id}
                        variants={itemVariants}
                        animate="visible"
                        whileHover={{ y: -4, transition: { duration: 0.2 } }}
                        className={`bg-white dark:bg-slate-900 p-6 rounded-2xl shadow-sm border transition-colors flex flex-col justify-between ${activePatientId === patient.id ? 'border-emerald-500 ring-1 ring-emerald-500 shadow-emerald-100/50 dark:shadow-none' : 'border-slate-100 dark:border-slate-800 hover:border-medical-200'}`}
                    >
                        <div>
                            <div className="flex justify-between items-start mb-4">
                                <div className="h-12 w-12 rounded-xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-500 dark:text-slate-400">
                                    <User className="h-6 w-6" />
                                </div>
                                {activePatientId === patient.id && (
                                    <span className="bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400 text-xs font-bold px-3 py-1 rounded-full flex items-center">
                                        <ShieldCheck className="w-3 h-3 mr-1" /> Active
                                    </span>
                                )}
                            </div>
                            <h3 className="text-xl font-bold text-slate-800 dark:text-white mb-4">{patient.name}</h3>
                            
                            <div className="space-y-3 mb-6">
                                <div className="flex items-center text-sm font-medium text-slate-600 dark:text-slate-400">
                                    <Globe className="w-4 h-4 mr-3 text-slate-400" />
                                    <span>Prefers: <strong className="text-slate-800 dark:text-slate-200">{langMap[patient.language] || patient.language}</strong></span>
                                </div>
                                <div className="flex items-center text-sm font-medium text-slate-600 dark:text-slate-400">
                                    <Activity className="w-4 h-4 mr-3 text-slate-400" />
                                    <span>Condition: <strong className="text-slate-800 dark:text-slate-200">{patient.disability}</strong></span>
                                </div>
                            </div>
                            
                            <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-100 dark:border-slate-800">
                                <div>
                                    <p className="text-xs font-bold text-slate-400 uppercase">Sessions</p>
                                    <p className="text-lg font-black text-slate-800 dark:text-slate-200">{patient.totalSessions}</p>
                                </div>
                                <div>
                                    <p className="text-xs font-bold text-slate-400 uppercase">Last Visit</p>
                                    <p className="text-sm font-bold text-slate-800 dark:text-slate-200 mt-0.5">{patient.lastSession}</p>
                                </div>
                            </div>
                        </div>

                        {activePatientId !== patient.id && (
                            <button
                                onClick={() => handleSetActive(patient)}
                                className="w-full mt-6 py-2.5 bg-slate-50 dark:bg-slate-800 text-slate-600 dark:text-slate-300 font-bold rounded-xl hover:bg-medical-50 dark:hover:bg-medical-900/20 hover:text-medical-600 dark:hover:text-medical-400 transition-colors flex justify-center items-center"
                            >
                                Set Active <ChevronRight className="w-4 h-4 ml-1" />
                            </button>
                        )}
                    </motion.div>
                ))}
            </div>

            {/* Pagination Controls */}
            {totalPages > 1 && (
                <div className="flex items-center justify-between pt-6 border-t border-slate-100 dark:border-slate-800">
                    <p className="text-sm text-slate-500 dark:text-slate-400 font-medium">
                        Showing <span className="font-bold text-slate-800 dark:text-slate-200">{(currentPage - 1) * ITEMS_PER_PAGE + 1}</span> to <span className="font-bold text-slate-800 dark:text-slate-200">{Math.min(currentPage * ITEMS_PER_PAGE, filteredPatients.length)}</span> of <span className="font-bold text-slate-800 dark:text-slate-200">{filteredPatients.length}</span> patients
                    </p>
                    <div className="flex items-center space-x-2">
                        <button
                            disabled={currentPage === 1}
                            onClick={() => setCurrentPage(prev => prev - 1)}
                            className="p-2 rounded-xl border border-slate-200 dark:border-slate-800 text-slate-400 hover:text-medical-600 hover:bg-medical-50 dark:hover:bg-medical-900/20 disabled:opacity-30 disabled:hover:bg-transparent transition-all"
                        >
                            <ChevronLeft className="h-5 w-5" />
                        </button>
                        {[...Array(totalPages)].map((_, i) => (
                            <button
                                key={i}
                                onClick={() => setCurrentPage(i + 1)}
                                className={`h-10 w-10 rounded-xl font-bold transition-all ${currentPage === i + 1 ? 'bg-medical-600 text-white shadow-md' : 'text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-800'}`}
                            >
                                {i + 1}
                            </button>
                        ))}
                        <button
                            disabled={currentPage === totalPages}
                            onClick={() => setCurrentPage(prev => prev + 1)}
                            className="p-2 rounded-xl border border-slate-200 dark:border-slate-800 text-slate-400 hover:text-medical-600 hover:bg-medical-50 dark:hover:bg-medical-900/20 disabled:opacity-30 disabled:hover:bg-transparent transition-all"
                        >
                            <ChevronRight className="h-5 w-5" />
                        </button>
                    </div>
                </div>
            )}

            <AnimatePresence>
                {isMenuOpen && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4"
                    >
                        <motion.div
                            initial={{ scale: 0.95, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            exit={{ scale: 0.95, opacity: 0 }}
                            className="bg-white dark:bg-slate-900 rounded-3xl shadow-2xl w-full max-w-lg overflow-hidden border border-slate-200 dark:border-slate-800"
                        >
                            <div className="px-6 py-4 border-b border-slate-100 dark:border-slate-800 flex justify-between items-center bg-slate-50/50 dark:bg-slate-800/30">
                                <h2 className="text-xl font-bold text-slate-800 dark:text-white flex items-center">
                                    <Users className="w-5 h-5 mr-2 text-medical-600" />
                                    Register New Patient
                                </h2>
                                <button onClick={() => setIsMenuOpen(false)} className="p-2 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-slate-200 dark:border-slate-700">
                                    <X className="w-5 h-5" />
                                </button>
                            </div>
                            
                            <form onSubmit={handleCreate} className="p-6 space-y-6">
                                <div>
                                    <label className="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-2">Patient Full Name</label>
                                    <input 
                                        required 
                                        type="text" 
                                        value={form.name}
                                        onChange={e => setForm({...form, name: e.target.value})}
                                        className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-medical-500 focus:outline-none text-slate-800 dark:text-white"
                                        placeholder="e.g. Jane Smith"
                                    />
                                </div>
                                
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-2">Preferred Translation</label>
                                        <select 
                                            value={form.language}
                                            onChange={e => setForm({...form, language: e.target.value})}
                                            className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-medical-500 focus:outline-none text-slate-800 dark:text-white appearance-none"
                                        >
                                            <option value="en">English</option>
                                            <option value="te">Telugu</option>
                                            <option value="hi">Hindi</option>
                                            <option value="mr">Marathi</option>
                                            <option value="ta">Tamil</option>
                                        </select>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-2">Condition Focus</label>
                                        <select 
                                            value={form.disability}
                                            onChange={e => setForm({...form, disability: e.target.value})}
                                            className="w-full px-4 py-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-medical-500 focus:outline-none text-slate-800 dark:text-white appearance-none"
                                        >
                                            <option value="Deaf">Deaf</option>
                                            <option value="Mute">Mute</option>
                                            <option value="Both">Deaf & Mute</option>
                                        </select>
                                    </div>
                                </div>

                                <div className="pt-4 flex justify-end">
                                    <button 
                                        type="submit"
                                        className="px-6 py-3 bg-medical-600 dark:bg-medical-500 text-white rounded-xl font-bold hover:bg-medical-700 dark:hover:bg-medical-600 transition-all shadow-lg shadow-medical-200 dark:shadow-none"
                                    >
                                        Save Patient Profile
                                    </button>
                                </div>
                            </form>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
};

export default PatientView;
