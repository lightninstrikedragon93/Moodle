import { useRouter } from "next/navigation";
import { useState } from "react";

const API_BASE_URL_M3 = 'http://localhost:8002/api/academia_user';
const Settings: React.FC = () => {
    const [password, setPassword] = useState<string>('');
    const [newPassword, setNewPassword] = useState<string>('');
    const [error, setError] = useState<string>('');
    const router = useRouter();

    const changePassword = async (e: React.FormEvent<HTMLFormElement>) =>{
        e.preventDefault();
        setError('');

        const token = localStorage.getItem('token');
        if (!token) {
            setError('You must be logged in to change the password.');
            return;
        }

        const url = new URL(`${API_BASE_URL_M3}/change_password`);
        url.searchParams.append('old_password', password);  
        url.searchParams.append('new_password', newPassword); 

        const response = await fetch(url.toString(), {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': `Bearer ${token}`,  
            },
        });

        if (response.ok){
            localStorage.removeItem('token');
            router.push('/');
        }
        else{
            const errorData = await response.json();
            setError(errorData.detail || 'Error changing password');
        }
    };

    const getUserIdFromToken = (token: string): number | null => {
        try {
            const payload = token.split('.')[1];
            const decodedPayload = JSON.parse(atob(payload));
    
            // Extragem user_id din sub (exemplu: 'admin:1')
            const userId = decodedPayload.sub.split(':')[1];  // presupunând că sub este în format 'role:id'
            return parseInt(userId, 10);
        } catch (error) {
            console.error('Error extracting user ID from token:', error);
            return null;
        }
    };

    return (
        <div className="settings-container">
            <h1>Change Password</h1>
            {error && <p className="error">{error}</p>}
            <form onSubmit={changePassword}>
                <label htmlFor="password">Current Password:</label>
                <input
                    type="password"
                    id="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
                <label htmlFor="newPassword">New Password:</label>
                <input
                    type="password"
                    id="newPassword"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    required
                />
                <button type="submit">Change Password</button>
            </form>
        </div>
    );
    
}

export default Settings;