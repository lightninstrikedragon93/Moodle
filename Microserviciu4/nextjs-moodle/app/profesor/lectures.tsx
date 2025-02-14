import { useEffect, useState } from "react";
import { Lecture } from "../interfaces/lectures";
import PersonalInfo from "./personalInfo";
import { Materiale, MaterialeCreate } from "../interfaces/materiale";
import { Professor } from "../interfaces/professor";
import EditFormMateriale from "./FormMateriale";
import ConfirmDelete from "../admin/confirmDelete";
import { Evaluation, EvaluationCreate } from "../interfaces/evaluation";
import EditFormEvaluare from "./FormEvaluare";

const API_BASE_URL_M1 = 'http://localhost:8000';
const API_BASE_URL_M3 = 'http://localhost:8002/api/academia_user';

const Lectures: React.FC = () => {
    const [lectures, setLectures] = useState<Lecture []>([]);
    const [professor, setProfessor] = useState<Professor>();
    const [menuOpen, setMenuOpen] = useState<{ [key: string]: boolean }>({});
    const [labMaterials, setLabMaterials] = useState<Materiale []>([]);
    const [courseMaterials, setCourseMaterials] = useState<Materiale []>([]);
    const [evaluations, setEvaluation] = useState<Evaluation []>([])
    const [editingEntityC, setEditingEntityC] = useState<Materiale | null>(null);
    const [deletingEntityC, setDeletingEntityC] = useState<Materiale | null>(null);
    const [createEntityC, setCreateEntityC] = useState<MaterialeCreate | null>(null);
    const [editingEntityL, setEditingEntityL] = useState<Materiale | null>(null);
    const [deletingEntityL, setDeletingEntityL] = useState<Materiale | null>(null);
    const [createEntityL, setCreateEntityL] = useState<MaterialeCreate | null>(null);
    const [createEntityE, setCreateEntityE] = useState<EvaluationCreate | null>(null);
    const [deletingEntityE, setDeletingEntityE] = useState<Evaluation | null>(null);
    const [selectedLecture, setSelectedLecture] = useState<Lecture | null> (null);
    const [idProfesor, setIdProfesor] = useState<number>(1);
    const [codDisciplina, setCodDisciplina] = useState<string>('');
    const [materialType, setMaterialType] = useState<'curs' | 'laborator'>('curs');



    const fetchProfessor = async (token: string): Promise<number | null> => {
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

            const response = await fetch(`${API_BASE_URL_M1}/api/academia/professors/${username}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            if (response.ok) {
                const data = await response.json();
                setProfessor(data);
                return data.id; 
            } else {
                console.error('Failed to fetch professor:', response.statusText);
                return null;
            }
        } catch (error) {
            console.error('Error fetching profesor:', error);
            return null;
        }
    };

    const fetchLectures = async () => {
        const token = localStorage.getItem('token');
        if (!token) return;
        const id = await fetchProfessor(token);
        const response = await fetch(`${API_BASE_URL_M1}/api/academia/professors/${id}/lectures`, {
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
                `${API_BASE_URL_M1}/api/academia/professors/${id_profesor}/lectures/${cod_disciplina}/materiale_laborator`,
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
                `${API_BASE_URL_M1}/api/academia/professors/${id_profesor}/lectures/${cod_disciplina}/materiale_curs`,
                {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                }
            );
    
            if (response.ok) {
                const data = await response.json();
                setCourseMaterials(prev => ({ ...prev, [cod_disciplina]: data }));
            } else {
                console.error('Failed to fetch materials:', response.statusText);
            }            } catch (error) {
            console.error('Error fetching materials:', error);
        }
    };

    const fetchEvaluare = async (id_profesor: number, cod_disciplina: string) => {
        const token = localStorage.getItem('token');
        if (!token) return;
    
        try {
            const response = await fetch(
                `${API_BASE_URL_M1}/api/academia/professors/${id_profesor}/lectures/${cod_disciplina}/evaluare`,
                {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                }
            );
    
            if (response.ok) {
                const data = await response.json();
                console.log(data);
                setEvaluation(data);
            } else {
                console.error('Failed to fetch evaluare:', response.statusText);
            }            } catch (error) {
            console.error('Error fetching evaluare:', error);
        }
    };

    const toggleMenuLecture = (lecture: Lecture) => {
        setMenuOpen(prev => ({ ...prev, [lecture.cod]: !prev[lecture.cod] }));
    };

    const toggleMenuMaterial = (material: Materiale) => {
        setMenuOpen(prev => ({ ...prev, [material.titlu]: !prev[material.titlu] }));
    };

    const handleEditC = (materiale: Materiale) => {
        setEditingEntityC(materiale); 
    };

    const handleDeleteC = (materiale: Materiale) => {
        setDeletingEntityC(materiale);
    };

    const handleEditL = (materiale: Materiale) => {
        setEditingEntityL(materiale); 
    };

    const handleDeleteL = (materiale: Materiale) => {
        setDeletingEntityL(materiale);
    };
    const handleCreateC = () => {
        setCreateEntityC({
            titlu: 'Titlu Material',
            capitol: 1,
            saptamana: 1,
            continut: 'continut',
        });
    };
    const handleCreateL = () => {
        setCreateEntityL({
            titlu: 'Titlu Material',
            capitol: 1,
            saptamana: 1,
            continut: 'continut',
        });
    };

    const handleCreateE = () => {
        setCreateEntityE({
            tip: 'Tip',
            pondere: 1,
        });
    };

    const handleDeleteE = (evaluare: Evaluation) => {
        setDeletingEntityE(evaluare);
        console.log('Deleting entity:', evaluare);
    };

    // useEffect(() => {
    //     if (idProfesor && codDisciplina) {
    //         fetchMaterialeCurs(idProfesor, codDisciplina);
    //     }
    // }, [idProfesor, codDisciplina]);

    const handleUpdateMaterialeCurs = (materiale: Materiale | MaterialeCreate) => {
        if ('links' in materiale) {
            const updateLink = materiale.links.update.href;
            const token = localStorage.getItem('token');
            if (!token) return;
    
            const {links, ...dataToUpdate } = materiale;
    
            fetch(`${API_BASE_URL_M1}${updateLink}`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(dataToUpdate),
            })
            .then(response => {
                if (response.ok) {
                    setEditingEntityC(null);
                } else {
                    console.error('Failed to update student:', response.statusText);
                }
            })
            .catch(error => {
                console.error('Error updating student:', error);
            });
        } else {
            console.error('Invalid materiale object for update');
        }
    };

    const handleDeleteMaterialCurs = (id_profesor: number, cod_disciplina: string) => {
        if (deletingEntityC) {
            const deleteLink = deletingEntityC.links.delete.href;
            console.log(deleteLink);
            const materialTitle = deletingEntityC.titlu;
            const token = localStorage.getItem('token');
            if (!token || !materialTitle) return;

            fetch(`${API_BASE_URL_M1}${deleteLink}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            })
            .then(async (response) => {
                if (response.ok) {
                    setDeletingEntityC(null);
                    fetchMaterialeCurs(id_profesor, cod_disciplina);
                } else {
                    const text = await response.text();
                    console.error('Failed to delete materiale:', response.statusText, text);
                }
            })
            .catch((error) => {
                console.error('Error deleting materiale:', error);
            });
        }
    };

    const handleCreateNewMaterialeCurs = async (id_profesor: number, cod_disciplina: string, material: MaterialeCreate) => {
        console.log("Data to the api:", material);
        const materialLink = `${API_BASE_URL_M1}/api/academia/professors/${id_profesor}/lectures/${cod_disciplina}/materiale_curs`
        const token = localStorage.getItem('token');
        if (!token) return;

        fetch(materialLink, { 
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(material),
        })
        .then(async response => {
            if (response.ok) {
                setCreateEntityC(null);
                fetchMaterialeCurs(id_profesor, cod_disciplina);
            } else {
                const text = await response.text();
                console.error('Failed to create materiale:', response.statusText, text);
            }
        })
        .catch(error => {
            console.error('Error creating materiale:', error);
        });
    }

    const handleUpdateMaterialeLaborator = (materiale: Materiale | MaterialeCreate) => {
        console.log("data receive:", materiale);
        if ('links' in materiale) {
            const updateLink = materiale.links.update.href;
            const token = localStorage.getItem('token');
            if (!token) return;
    
            const {links, ...dataToUpdate } = materiale;
    
            fetch(`${API_BASE_URL_M1}${updateLink}`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(dataToUpdate),
            })
            .then(response => {
                if (response.ok) {
                    setEditingEntityL(null);
                } else {
                    console.error('Failed to update materiale:', response.statusText);
                }
            })
            .catch(error => {
                console.error('Error updating materiale:', error);
            });
        } else {
            console.error('Invalid materiale object for update');
        }
    };

    const handleDeleteMaterialLaborator = (id_profesor: number, cod_disciplina: string) => {
        if (deletingEntityC) {
            const deleteLink = deletingEntityC.links.delete.href;
            console.log(deleteLink);
            const materialTitle = deletingEntityC.titlu;
            const token = localStorage.getItem('token');
            if (!token || !materialTitle) return;

            fetch(`${API_BASE_URL_M1}${deleteLink}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            })
            .then(async (response) => {
                if (response.ok) {
                    setDeletingEntityL(null);
                    fetchMaterialeLaborator(id_profesor, cod_disciplina);
                } else {
                    const text = await response.text();
                    console.error('Failed to delete materiale:', response.statusText, text);
                }
            })
            .catch((error) => {
                console.error('Error deleting materiale:', error);
            });
        }
    };

    const handleCreateNewMaterialeLaborator = async (id_profesor: number, cod_disciplina: string, material: MaterialeCreate) => {
        console.log("Data to the api:", material);
        const materialLink = `${API_BASE_URL_M1}/api/academia/professors/${id_profesor}/lectures/${cod_disciplina}/materiale_laborator`
        const token = localStorage.getItem('token');
        if (!token) return;

        fetch(materialLink, { 
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(material),
        })
        .then(async response => {
            if (response.ok) {
                setCreateEntityL(null);
                fetchMaterialeLaborator(id_profesor, cod_disciplina);
            } else {
                const text = await response.text();
                console.error('Failed to create materiale:', response.statusText, text);
            }
        })
        .catch(error => {
            console.error('Error creating materiale:', error);
        });
        console.log(material);
    }

    const handleDeleteEvaluare = (id_profesor: number, cod_disciplina: string) => {
        if (deletingEntityE) {
            const deleteLink = deletingEntityE.links.delete.href;
            const evaluationTip = deletingEntityE?.tip;
            const token = localStorage.getItem('token');
            if (!token || !evaluationTip) return;

            fetch(`${API_BASE_URL_M1}${deleteLink}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            })
            .then(async (response) => {
                if (response.ok) {
                    setDeletingEntityE(null);
                    fetchEvaluare(id_profesor, cod_disciplina);
                } else {
                    const text = await response.text();
                    console.error('Failed to delete evaluare:', response.statusText, text);
                }
            })
            .catch((error) => {
                console.error('Error deleting evaluare:', error);
            });
        }
    };

    const handleCreateNewEvaluare = async (evaluare: EvaluationCreate) => {
        console.log("data receive:", evaluare);
        const evaluareLink = `${API_BASE_URL_M1}/api/academia/professors/${idProfesor}/lectures/${codDisciplina}/evaluare`
        const token = localStorage.getItem('token');
        if (!token) return;

        fetch(evaluareLink, { 
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(evaluare),
        })
        .then(async response => {
            if (response.ok) {
                setCreateEntityE(null);
                fetchEvaluare(idProfesor, codDisciplina);
            } else {
                const text = await response.text();
                console.error('Failed to create evaluare:', response.statusText, text);
            }
        })
        .catch(error => {
            console.error('Error creating evaluare:', error);
        });
    };

    useEffect(() => {
        console.log("CreateEntityL updated:", createEntityE);
      }, [createEntityE]);

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
                                        <button onClick={() => toggleMenuLecture(lecture)}>⋮</button>
                                            {menuOpen[lecture.cod] && (
                                                <div className="menu">
                                                    <button onClick={() => {
                                                        setIdProfesor(lecture.id_titular),
                                                        setCodDisciplina(lecture.cod),
                                                        fetchMaterialeLaborator(idProfesor, codDisciplina), 
                                                        setSelectedLecture(lecture), 
                                                        setMaterialType('laborator')}}
                                                        >Materiale Laborator</button>
                                                    <button onClick={() => {
                                                        fetchMaterialeCurs(lecture.id_titular, lecture.cod),
                                                         setSelectedLecture(lecture), 
                                                         setMaterialType('curs')}}
                                                         >Materiale Curs</button>
                                                    <button onClick={() => {
                                                        setIdProfesor(lecture.id_titular),
                                                        setCodDisciplina(lecture.cod),
                                                        fetchEvaluare(idProfesor,codDisciplina), 
                                                        setSelectedLecture(lecture)}}
                                                        >Evaluare</button>
                                                </div>
                                            )}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                        {selectedLecture && (
                            <div>
                                <button onClick={() => {
                                    if (materialType === 'curs') {
                                        handleCreateC();
                                    } else {
                                        handleCreateL();
                                    }
                                }}>
                                    Add Material
                                </button>
                                <button onClick={() =>{
                                        handleCreateE();
                                }}>Add Evaluare</button>
                            </div>
                        )}
                        {Object.entries(labMaterials).map(([cod_disciplina, materials]) => (
                            <div key={cod_disciplina}>

                                <ul>
                                    {Array.isArray(materials) ? materials.map((material, index) => (
                                        <li key={index}>
                                            <h3>{material.titlu}</h3>
                                            <button onClick={() => toggleMenuMaterial(material)}>⋮</button>
                                            {menuOpen[material.titlu] && (
                                                <div className="menu">
                                                    <button onClick={() => handleEditL(material)}>Edit</button>
                                                    <button onClick={() => handleDeleteL(material)}>Delete</button>
                                                </div>
                                            )}
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
                                        <button onClick={() => toggleMenuMaterial(material)}>⋮</button>
                                            {menuOpen[material.titlu] && (
                                                <div className="menu">
                                                    <button onClick={() => handleEditC(material)}>Edit</button>
                                                    <button onClick={() => handleDeleteC(material)}>Delete</button>
                                                </div>
                                            )}
                                        <p>Capitol: {material.capitol}</p>
                                        <p>Saptamana: {material.saptamana}</p>
                                        <p>Continut: {material.continut}</p>
                                    </li>
                                )) : <li>No materials available</li>}
                            </ul>
                        </div>
                        ))}
                        {/* {Object.entries(evaluations).map(([cod_disciplina, evaluationsArray]) => (
                        <div key={cod_disciplina}> */}
                            <ul>
                                {Array.isArray(evaluations) ? evaluations.map((evaluationItem, index) => (
                                    <li key={index}>
                                        <h3>{evaluationItem.tip}</h3>
                                        <button onClick={() => handleDeleteE(evaluationItem)}>Delete</button>
                                        <p>Tip: {evaluationItem.tip}</p>
                                        <p>Pondere: {evaluationItem.pondere}</p>
                                    </li>
                                )) : <li>No evaluation available</li>}
                            </ul>
                        {/* </div> */}
                        
                    

                        {editingEntityC && (
                        <EditFormMateriale
                            entity={editingEntityC}
                            onSave={handleUpdateMaterialeCurs} 
                            onCancel={() => setEditingEntityC(null)}
                        />
                        )}
                        {deletingEntityC && (
                            <ConfirmDelete
                                onConfirm={() => handleDeleteMaterialCurs(selectedLecture?.id_titular || 0, selectedLecture?.cod || '')} 
                                onCancel={() => setDeletingEntityC(null)}
                            />
                        )}
                        {createEntityC && (
                        <EditFormMateriale
                            entity={createEntityC}
                            onSave={() => handleCreateNewMaterialeCurs(selectedLecture?.id_titular || 0, selectedLecture?.cod || '', createEntityC)} 
                            onCancel={() => setCreateEntityC(null)}
                        />)}

                        {editingEntityL && (
                        <EditFormMateriale
                            entity={editingEntityL}
                            onSave={handleUpdateMaterialeLaborator} 
                            onCancel={() => setEditingEntityL(null)}
                        />
                        )}
                        {deletingEntityL && (
                            <ConfirmDelete
                                onConfirm={() => handleDeleteMaterialLaborator(selectedLecture?.id_titular || 0, selectedLecture?.cod || '')} 
                                onCancel={() => setDeletingEntityL(null)}
                            />
                        )}
                        {createEntityL && (
                        <EditFormMateriale
                            entity={createEntityL}
                            onSave={() => handleCreateNewMaterialeLaborator(selectedLecture?.id_titular || 0, selectedLecture?.cod || '', createEntityL)} 
                            onCancel={() => setCreateEntityL(null)}
                        />)}

                        {deletingEntityE && (
                            <ConfirmDelete
                                onConfirm={() => handleDeleteEvaluare(selectedLecture?.id_titular || 0, selectedLecture?.cod || '')} 
                                onCancel={() => setDeletingEntityE(null)}
                            />
                        )}
                        {createEntityE && (
                        <EditFormEvaluare
                            entity={createEntityE}
                            onSave={handleCreateNewEvaluare} 
                            onCancel={() => setCreateEntityE(null)}
                        />)}
                    </div>
                )}
        </div>
    );
};

export default Lectures;