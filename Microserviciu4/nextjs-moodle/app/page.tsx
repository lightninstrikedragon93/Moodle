'use client'

import { useState } from 'react';
import { useRouter } from 'next/navigation';

const Login: React.FC = () => {
    const [username, setUsername] = useState<string>('');
    const [password, setPassword] = useState<string>('');
    const [error, setError] = useState<string>('');
    const router = useRouter();

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setError('');

        const res = await fetch('http://localhost:8002/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({
                username,
                password,
            }),
        });

        if (res.ok) {
            const data = await res.json();
            const token = data.access_token;
            localStorage.setItem('token', token);

            const role = getRoleFromToken(token);
            redirectToPage(role);
        } else {
            const errorData = await res.json();
            setError(errorData.detail || 'Invalid credentials');
        }
    };

    const getRoleFromToken = (token: string): string => {
        try {
            const payload = token.split('.')[1];
            const decodedPayload = JSON.parse(atob(payload));
            return decodedPayload.role;
        } catch (error) {
            console.error('Error extracting role from token:', error);
            return '';
        }
    };

    const redirectToPage = (role: string) => {
        if (role === 'admin') {
            router.push('/admin'); 
        } else if (role === 'student') {
            router.push('/student'); 
        } else if (role === 'profesor') {
            router.push('/profesor');
        } else {
            console.error('Unknown role:', role);
        }
    };

    return (
        <div className="login-container">
            <h1>Login</h1>
            {error && <p className="error">{error}</p>}
            <form onSubmit={handleSubmit}>
                <label htmlFor="username">Username/Email:</label>
                <input
                    type="text"
                    id="username"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                    required
                />
                <label htmlFor="password">Password:</label>
                <input
                    type="password"
                    id="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
                <button type="submit">Login</button>
            </form>
        </div>
    );
};

export default Login;