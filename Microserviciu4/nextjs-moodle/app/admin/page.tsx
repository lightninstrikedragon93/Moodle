"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Students from './students';
import Professors from './professors';
import Lectures from './lectures';
import Settings from './settings';


const Admin: React.FC = () => {
    const [activeTab, setActiveTab] = useState<string>('students');
    const router = useRouter();

    const handleLogout = () => {
        localStorage.removeItem('token');
        router.push('/');
    };

    const renderContent = () => {
        switch (activeTab) {
            case 'students':
                return (
                    <div>
                        <Students/>
                    </div>
                );
            case 'professors':
                return (
                    <div>
                        <Professors/>
                    </div>
                );
            case 'settings':
                return <Settings/>
            case 'lectures':
                return <Lectures/>
            default:
                return <div>Select an option from the sidebar</div>;
        }
    };

    return (
        <div className="admin-container" style={{ display: 'flex', flexDirection: 'row' }}>
            <aside className="sidebar" style={{ width: '200px', padding: '20px', borderRight: '1px solid #ccc'}}>
                <h2>Admin Panel</h2>
                <ul>
                    <li onClick={() => setActiveTab('students')} style={{ cursor: 'pointer' }}>Students</li>
                    <li onClick={() => setActiveTab('professors')} style={{ cursor: 'pointer' }}>Professors</li>
                    <li onClick={() => setActiveTab('lectures')} style={{ cursor: 'pointer' }}>Lectures</li>
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

export default Admin;