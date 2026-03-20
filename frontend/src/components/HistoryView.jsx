import React, { useState } from 'react';
import { generateSessionPDF } from '../utils/pdfExport';
import {
    FileText,
    Download,
    Search,
    Filter,
    Play,
    MoreHorizontal,
    ChevronLeft,
    ChevronRight,
    ExternalLink
} from 'lucide-react';

const HistoryView = () => {
    const initialLogs = [
        { id: 1, term: 'Heart Attack', confidence: 0.982, time: '2026-02-15 19:42:11', source: 'Webcam', status: 'Success', patientId: 'p1', patientName: 'John Doe' },
        { id: 2, term: 'Diabetes', confidence: 0.854, time: '2026-02-15 19:38:05', source: 'Upload', status: 'Success', patientId: 'p2', patientName: 'Maria Garcia' },
        { id: 3, term: 'Broken Arm', confidence: 0.991, time: '2026-02-15 19:12:45', source: 'Webcam', status: 'Success', patientId: 'p1', patientName: 'John Doe' },
        { id: 4, term: 'Emergency', confidence: 0.923, time: '2026-02-15 18:55:30', source: 'Upload', status: 'Success', patientId: null, patientName: 'Guest' },
        { id: 5, term: 'Hospital', confidence: 0.782, time: '2026-02-15 18:30:12', source: 'Webcam', status: 'Success', patientId: 'p2', patientName: 'Maria Garcia' },
        { id: 6, term: 'Pain', confidence: 0.945, time: '2026-02-15 18:15:00', source: 'Webcam', status: 'Success', patientId: 'p1', patientName: 'John Doe' },
        { id: 7, term: 'Medication', confidence: 0.887, time: '2026-02-15 17:45:22', source: 'Upload', status: 'Success', patientId: null, patientName: 'Guest' },
    ];

    const [logs, setLogs] = React.useState([]);
    const [patients, setPatients] = React.useState([]);
    const [selectedPatient, setSelectedPatient] = React.useState('all');
    const [searchQuery, setSearchQuery] = React.useState('');

    React.useEffect(() => {
        const localHistory = JSON.parse(localStorage.getItem('medisign_history') || '[]');
        setLogs([...localHistory, ...initialLogs]);
        
        const localPatients = JSON.parse(localStorage.getItem('medisign_patients') || '[]');
        setPatients(localPatients);
    }, []);

    const filteredLogs = logs.filter(log => {
        const matchesSearch = log.term.toLowerCase().includes(searchQuery.toLowerCase()) || 
                              log.source.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesPatient = selectedPatient === 'all' || log.patientId === selectedPatient;
        return matchesSearch && matchesPatient;
    });

    const handleExportPDF = (e) => {
        e.preventDefault();
        try {
            let title = "Session Report: All Patients";
            if (selectedPatient === 'null') {
                title = "Session Report: Guest / Unassigned";
            } else if (selectedPatient !== 'all') {
                const pat = patients.find(p => p.id === selectedPatient);
                if (pat) title = `Session Report: ${pat.name}`;
            }
            generateSessionPDF(filteredLogs, title);
        } catch (error) {
            console.error("PDF Export Error:", error);
            alert("Error generating PDF. Please ensure your browser allows downloads.");
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Prediction Logs</h1>
                    <p className="text-slate-500 dark:text-slate-400 mt-1 font-medium italic">Audit trail of all sign language recognitions</p>
                </div>
                <div className="flex items-center space-x-3">
                    <button className="flex items-center space-x-2 px-4 py-2.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-700 dark:text-slate-200 font-semibold hover:bg-slate-50 dark:hover:bg-slate-700 transition-all shadow-sm">
                        <Download className="h-4 w-4" />
                        <span>Export CSV</span>
                    </button>
                    <button type="button" onClick={handleExportPDF} className="flex items-center space-x-2 px-4 py-2.5 bg-medical-600 dark:bg-medical-500 text-white rounded-xl font-semibold hover:bg-medical-700 dark:hover:bg-medical-600 transition-all shadow-lg shadow-medical-100 dark:shadow-none">
                        <FileText className="h-4 w-4" />
                        <span>Export Session PDF</span>
                    </button>
                </div>
            </div>

            <div className="bg-white dark:bg-slate-900 rounded-3xl shadow-sm border border-slate-100 dark:border-slate-800 overflow-hidden transition-colors">
                <div className="p-6 border-b border-slate-100 dark:border-slate-800 flex flex-col sm:flex-row bg-slate-50/50 dark:bg-slate-800/30 sm:items-center justify-between gap-4">
                    <div className="relative flex-1 max-w-md">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 dark:text-slate-500" />
                        <input
                            type="text"
                            placeholder="Search logs by medical term or source..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full pl-10 pr-4 py-2.5 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-medical-500 transition-all text-slate-900 dark:text-slate-100"
                        />
                    </div>
                    <div className="flex items-center space-x-3">
                        <select
                            value={selectedPatient}
                            onChange={(e) => setSelectedPatient(e.target.value)}
                            className="px-3 py-2 text-sm bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl text-slate-700 dark:text-slate-200 focus:outline-none focus:ring-2 focus:ring-medical-500"
                        >
                            <option value="all">All Patients</option>
                            <option value="null">Guest / Unassigned</option>
                            {patients.map(p => (
                                <option key={p.id} value={p.id}>{p.name}</option>
                            ))}
                        </select>
                        <button className="p-2.5 text-slate-500 dark:text-slate-400 hover:text-medical-600 dark:hover:text-medical-400 hover:bg-medical-50 dark:hover:bg-medical-500/10 rounded-xl transition-all border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800">
                            <Filter className="h-5 w-5" />
                        </button>
                        <div className="h-6 w-px bg-slate-200 dark:bg-slate-700 mx-1"></div>
                        <span className="text-sm font-bold text-slate-400 dark:text-slate-500">Total: {filteredLogs.length}</span>
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="bg-slate-50/50 dark:bg-slate-800/20 border-b border-slate-100 dark:border-slate-800">
                                <th className="px-6 py-4 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest">Medical Term</th>
                                <th className="px-6 py-4 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest">Patient</th>
                                <th className="px-6 py-4 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest">Confidence</th>
                                <th className="px-6 py-4 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest">Date & Time</th>
                                <th className="px-6 py-4 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest">Source</th>
                                <th className="px-6 py-4 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-widest text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-50 dark:divide-slate-800">
                            {filteredLogs.map((log) => (
                                <tr key={log.id} className="hover:bg-medical-50/30 dark:hover:bg-medical-500/10 transition-colors group">
                                    <td className="px-6 py-4">
                                        <div className="flex items-center">
                                            <div className="h-2 w-2 rounded-full bg-medical-500 dark:bg-medical-400 mr-3"></div>
                                            <span className="font-bold text-slate-700 dark:text-slate-200">{log.term}</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className="text-sm font-medium text-slate-600 dark:text-slate-300">
                                            {log.patientName || 'Guest'}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4">
                                        <div className="flex items-center space-x-2">
                                            <div className="w-24 bg-slate-100 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden">
                                                <div
                                                    className={`h-full rounded-full ${log.confidence > 0.9 ? 'bg-emerald-500' : 'bg-amber-500'}`}
                                                    style={{ width: `${log.confidence * 100}%` }}
                                                ></div>
                                            </div>
                                            <span className="text-sm font-bold text-slate-600 dark:text-slate-400">{(log.confidence * 100).toFixed(1)}%</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className="text-sm font-medium text-slate-500 dark:text-slate-400">{log.time}</span>
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-md text-xs font-bold bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                                            {log.source}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        <div className="flex items-center justify-end space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                            <button className="p-2 text-slate-400 dark:text-slate-500 hover:text-medical-600 dark:hover:text-medical-400 hover:bg-medical-100 dark:hover:bg-medical-500/10 rounded-lg">
                                                <Play className="h-4 w-4" />
                                            </button>
                                            <button className="p-2 text-slate-400 dark:text-slate-500 hover:text-medical-600 dark:hover:text-medical-400 hover:bg-medical-100 dark:hover:bg-medical-500/10 rounded-lg">
                                                <ExternalLink className="h-4 w-4" />
                                            </button>
                                            <button className="p-2 text-slate-400 dark:text-slate-500 hover:text-slate-600 dark:hover:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-lg">
                                                <MoreHorizontal className="h-4 w-4" />
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                <div className="p-6 bg-slate-50/50 dark:bg-slate-800/30 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
                    <span className="text-sm font-semibold text-slate-500 dark:text-slate-400">Showing {Math.min(7, filteredLogs.length)} of {filteredLogs.length} results</span>
                    <div className="flex items-center space-x-2">
                        <button className="p-2 text-slate-400 dark:text-slate-600 cursor-not-allowed">
                            <ChevronLeft className="h-5 w-5" />
                        </button>
                        <button className="p-2 text-medical-600 dark:text-medical-400 bg-white dark:bg-slate-800 border border-medical-200 dark:border-medical-900/50 rounded-lg shadow-sm font-bold px-4 hover:bg-medical-50 dark:hover:bg-medical-500/10 transition-colors">
                            1
                        </button>
                        <button className="p-2 text-slate-600 dark:text-slate-400 hover:bg-white dark:hover:bg-slate-800 hover:shadow-sm dark:hover:shadow-none rounded-lg px-4 transition-all">
                            2
                        </button>
                        <button className="p-2 text-slate-500 dark:text-slate-400">
                            <ChevronRight className="h-5 w-5" />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default HistoryView;
