"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import Settings from "../admin/settings";
import Lectures from "./lectures";
import PersonalInfo from "./personalInfo";

const Dashboard: React.FC = () => {
    const [activeTab, setActiveTab] = useState<string>('lectures');
    const router = useRouter();

    const handleLogout = () => {
        localStorage.removeItem('token');
        router.push('/');
    };

    const renderContent = () => {
        switch (activeTab) {
            case 'settings':
                return <Settings/>
            case 'lectures':
                return <Lectures/>
            case 'personalInfo':
                return <PersonalInfo/>
            default:
                return <div>Select an option from the sidebar</div>;
        }
    };

    return (
        <div className="admin-container" style={{ display: 'flex', flexDirection: 'row' }}>
            <aside className="sidebar" style={{ width: '200px', padding: '20px', borderRight: '1px solid #ccc' }}>
                <h2>Panel</h2>
                <ul>
                    <li onClick={() => setActiveTab('lectures')} style={{ cursor: 'pointer' }}>Lectures</li>
                    <li onClick={() => setActiveTab('personalInfo')} style={{ cursor: 'pointer' }}>Personal Information</li>
                    <li onClick={() => setActiveTab('settings')} style={{ cursor: 'pointer' }}>Settings</li>
                    <button onClick={handleLogout} style={{ cursor: 'pointer'}}>Logout</button>
                </ul>
            </aside>
            <main className="content" style={{ padding: '20px', flexGrow: 1 }}>
                {renderContent()}
                
            </main>
        </div>
    );
};

export default Dashboard;