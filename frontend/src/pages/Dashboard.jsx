import React from 'react';
import DashboardLayout from '../layouts/DashboardLayout';
import WebcamView from '../components/WebcamView';
import UploadView from '../components/UploadView';
import HistoryView from '../components/HistoryView';
import Overview from '../components/Overview';
import AboutView from '../components/AboutView';
import PatientView from '../components/PatientView';

import Settings from '../components/Settings';
import InterpreterView from '../components/InterpreterView';
import CommunicationBridge from '../components/CommunicationBridge';

const Dashboard = ({ view = 'overview' }) => {
    const renderView = () => {
        switch (view) {
            case 'webcam':
                return <WebcamView />;
            case 'upload':
                return <UploadView />;
            case 'history':
                return <HistoryView />;
            case 'about':
                return <AboutView />;
            case 'patients':
                return <PatientView />;
            case 'settings':
                return <Settings />;
            case 'interpreter':
                return <InterpreterView />;
            case 'bridge':
                return <CommunicationBridge />;
            default:
                return <Overview />;
        }
    };

    return (
        <DashboardLayout>
            <div className="animate-in fade-in duration-500">
                {renderView()}
            </div>
        </DashboardLayout>
    );
};

export default Dashboard;
