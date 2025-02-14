import { useState } from "react";
import { Professor } from "../interfaces/professor";

const API_BASE_URL_M1 = 'http://localhost:8000/api/academia/professors';
const API_BASE_URL_M3 = 'http://localhost:8002/api/academia_user';

const PersonalInfo: React.FC = () => {
    const [professor, setProfessor] = useState<Professor>();

    const fecthProfessor = async () => {
        const token = localStorage.getItem('token');
        if (!token) return;

        try{
            const userId = getUserIdFromToken(token);
            const userResponse = await fetch(`${API_BASE_URL_M3}?user_id=${userId}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            if (!userResponse.ok) {
                console.error('Failed to fetch user data:', userResponse.statusText);
                return;
            }

            const userData = await userResponse.json();
            const username = userData.username;

            const response = await fetch(`${API_BASE_URL_M1}/${username}`, { 
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            if (response.ok) {
                const data = await response.json();
                setProfessor(data);
            } else {
                console.error('Failed to fetch student:', response.statusText);
            }
        } catch (error) {
            console.error('Error fetching student:', error);
        }
    };

    const getUserIdFromToken = (token: string) => {
        const payload = JSON.parse(atob(token.split('.')[1]));  
        const sub = payload.sub; 
        const userId = sub.split(':')[1];
        return userId;
    };

    return(
        <div>
            <button onClick={fecthProfessor}>Show information</button>
            <li>Nume: {professor?.nume}</li>
            <li>Prenume: {professor?.prenume}</li>
            <li>Email: {professor?.email}</li>
            <li>Grad Didactic: {professor?.grad_didactic}</li>
            <li>Asociere: {professor?.tip_asociere}</li>
            <li>Afiliere: {professor?.afiliere}</li>
        </div>
    );
};

export default PersonalInfo;