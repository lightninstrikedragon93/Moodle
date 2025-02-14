import { useState } from "react";
import { Lecture } from "../interfaces/lectures";
import PersonalInfo from "./personalInfo";
import { Student } from "../interfaces/student";
import { Materiale } from "../interfaces/materiale";

const API_BASE_URL_M1 = 'http://localhost:8000/api/academia';
const API_BASE_URL_M3 = 'http://localhost:8002/api/academia_user';

const Lectures: React.FC = () => {
    const [lectures, setLectures] = useState<Lecture []>([]);
    const [student, setStudent] = useState<Student>();
    const [menuOpen, setMenuOpen] = useState<{ [key: string]: boolean }>({});
    const [labMaterials, setLabMaterials] = useState<Materiale []>([]);
    const [courseMaterials, setCourseMaterials] = useState<Materiale []>([]);

    const fetchStudent = async (token: string): Promise<number | null> => {
        try {
            const userId = getUserIdFromToken(token);

            const userResponse = await fetch(`${API_BASE_URL_M3}?user_id=${userId}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            if (!userResponse.ok) {
                console.error('Failed to fetch user data:', userResponse.statusText);
                return null;
            }

            const userData = await userResponse.json();
            const username = userData.username;

            const response = await fetch(`${API_BASE_URL_M1}/students/${username}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            if (response.ok) {
                const data = await response.json();
                setStudent(data);
                return data.id; 
            } else {
                console.error('Failed to fetch student:', response.statusText);
                return null;
            }
        } catch (error) {
            console.error('Error fetching student:', error);
            return null;
        }
    };

    const fetchLectures = async () => {
        const token = localStorage.getItem('token');
        if (!token) return;
        const id = await fetchStudent(token);
        const response = await fetch(`${API_BASE_URL_M1}/students/${id}/lectures`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
            },
        });

        if (response.ok) {
            const data = await response.json();
            setLectures(data);
        } else {
            console.error('Failed to fetch lectures:', response.statusText);
        }
    };

    const getUserIdFromToken = (token: string) => {
        const payload = JSON.parse(atob(token.split('.')[1]));  
        const sub = payload.sub; 
        const userId = sub.split(':')[1];
        return userId;
    }

    const fetchMaterialeLaborator = async (id_profesor: number, cod_disciplina: string) => {
        const token = localStorage.getItem('token');
        if (!token) return;
    
        try {
            const response = await fetch(
                `${API_BASE_URL_M1}/professors/${id_profesor}/lectures/${cod_disciplina}/materiale_laborator`,
                {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                }
            );
    
            if (response.ok) {
                const data = await response.json();
                console.log('Received materials:', data);
                setLabMaterials(prev => ({ ...prev, [cod_disciplina]: data }));
            } else {
                console.error('Failed to fetch materials:', response.statusText);
            }            } catch (error) {
            console.error('Error fetching materials:', error);
        }
    };

    const fetchMaterialeCurs = async (id_profesor: number, cod_disciplina: string) => {
        const token = localStorage.getItem('token');
        if (!token) return;
    
        try {
            const response = await fetch(
                `${API_BASE_URL_M1}/professors/${id_profesor}/lectures/${cod_disciplina}/materiale_curs`,
                {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                }
            );
    
            if (response.ok) {
                const data = await response.json();
                console.log('Received materials:', data);
                setCourseMaterials(prev => ({ ...prev, [cod_disciplina]: data }));
            } else {
                console.error('Failed to fetch materials:', response.statusText);
            }            } catch (error) {
            console.error('Error fetching materials:', error);
        }
    };

    const toggleMenu = (lecture: Lecture) => {
        setMenuOpen(prev => ({ ...prev, [lecture.cod]: !prev[lecture.cod] }));
    };

    return (
        <div>
            <button onClick={fetchLectures}>Show Lectures</button>
                {lectures.length > 0 && (
                    <div>
                        <table>
                            <thead>
                                <tr>
                                    <th>Cod</th>
                                    <th>Titular</th>
                                    <th>Nume</th>
                                    <th>An Studiu</th>
                                    <th>Tip Disciplina</th>
                                    <th>Categorie</th>
                                    <th>Tip Examinare</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {lectures.map((lecture) =>(
                                    <tr key={lecture.cod}>
                                        <td>{lecture.cod}</td>
                                        <td>{lecture.id_titular}</td>
                                        <td>{lecture.nume_disciplina}</td>
                                        <td>{lecture.an_studiu}</td>
                                        <td>{lecture.tip_disciplina}</td>
                                        <td>{lecture.categorie_disciplina}</td>
                                        <td>{lecture.tip_examinare}</td>
                                        <td>
                                        <button onClick={() => toggleMenu(lecture)}>⋮</button>
                                            {menuOpen[lecture.cod] && (
                                                <div className="menu">
                                                    <button onClick={() => fetchMaterialeLaborator(lecture.id_titular, lecture.cod)}>Materiale Laborator</button>
                                                    <button onClick={() => fetchMaterialeCurs(lecture.id_titular, lecture.cod)}>Materiale Curs</button>
                                                </div>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                        {Object.entries(labMaterials).map(([cod_disciplina, materials]) => (
                            <div key={cod_disciplina}>

                                <ul>
                                    {Array.isArray(materials) ? materials.map((material, index) => (
                                        <li key={index}>
                                            <h3>{material.titlu}</h3>
                                            <p>Capitol: {material.capitol}</p>
                                            <p>Saptamana: {material.saptamana}</p>
                                            <p>Continut: {material.continut}</p>
                                        </li>
                                    )) : <li>No materials available</li>}
                                </ul>
                            </div>
                        ))}
                        {Object.entries(courseMaterials).map(([cod_disciplina, materials]) => (
                        <div key={cod_disciplina}>
                            <ul>
                                {Array.isArray(materials) ? materials.map((material, index) => (
                                    <li key={index}>
                                        <h3>{material.titlu}</h3>
                                        <p>Capitol: {material.capitol}</p>
                                        <p>Saptamana: {material.saptamana}</p>
                                        <p>Continut: {material.continut}</p>
                                    </li>
                                )) : <li>No materials available</li>}
                            </ul>
                        </div>
                    ))}
                    </div>
                )} 
        </div>
    );
};

export default Lectures;