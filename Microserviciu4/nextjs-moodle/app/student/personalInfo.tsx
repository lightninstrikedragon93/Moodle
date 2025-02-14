import { useState } from "react";
import { Student } from "../interfaces/student";

const API_BASE_URL_M1 = 'http://localhost:8000/api/academia/students';
const API_BASE_URL_M3 = 'http://localhost:8002/api/academia_user';

const PersonalInfo: React.FC = () =>{

    const [student, setStudent] = useState<Student>();

    const fecthStudent = async () => {
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
                setStudent(data);
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
    }

    return(
        <div>
            <button onClick={fecthStudent}>Show information</button>
            <li>Nume: {student?.nume}</li>
            <li>Prenume: {student?.prenume}</li>
            <li>Email: {student?.email}</li>
            <li>An studiu: {student?.an_studii}</li>
            <li>Ciclu studii: {student?.ciclu_studii}</li>
            <li>Grupa: {student?.grupa}</li>
        </div>
    );
};
export default PersonalInfo;