import React, { useEffect, useState } from 'react';
import { Professor, ProfessorCreate } from '../interfaces/professor';
import EditFormProfessor from './FormProfessor';
import ConfirmDelete from './confirmDelete';

const API_BASE_URL_M1 = 'http://localhost:8000';
const API_BASE_URL_M3 = 'http://localhost:8002/api/academia_user';

const Professors: React.FC = () => {
    const [professors, setProfessors] = useState<any[]>([]);
    const [currentPage, setCurrentPage] = useState<number>(1);
    const [itemsPerPage, setItemsPerPage] = useState<number>(5);
    const [menuOpen, setMenuOpen] = useState<{ [key: number]: boolean }>({});
    const [editingEntity, setEditingEntity] = useState<Professor | null>(null);
    const [deletingEntity, setDeletingEntity] = useState<Professor | null>(null);
    const [createEntity, setCreateEntity] = useState<Professor | null>(null);
    const [acadRank, setAcadRank] = useState<string>('');
    const [affiliation, setAffiliation] = useState<string>('');
    const [name, setName] = useState<string>('');
    
    const fetchProfessors = async () => {
        const token = localStorage.getItem('token');
        if (!token) return;

        const queryParams = new URLSearchParams();
        queryParams.append('skip', String((currentPage - 1) * itemsPerPage));
        queryParams.append('limit', String(itemsPerPage));
        if (acadRank) queryParams.append('acad_rank', acadRank);
        if (affiliation) queryParams.append('affiliation', affiliation);
        if (name) queryParams.append('name', name);

        try {
            const response = await fetch(`${API_BASE_URL_M1}/api/academia/professors?${queryParams.toString()}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            if (response.ok) {
                const data = await response.json();
                setProfessors(data);
            } else {
                console.error('Failed to fetch professors:', response.statusText);
            }
        } catch (error) {
            console.error('Error fetching professors:', error);
        }
    };


    const handleFilterChange = () => {
        fetchProfessors();

    }
    const handlePageChange = (page: number) => {
        setCurrentPage(page);       
        fetchProfessors();

    };

    const handleItemsPerPageChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        const newValue = Number(event.target.value)
        setItemsPerPage(newValue);
        setCurrentPage(1);
        fetchProfessors();
        
    };

    const handleEdit = (professor: Professor) => {
        setEditingEntity(professor); 
    };

    const handleDelete = (professor: Professor) => {
        setDeletingEntity(professor);
    };
    const handleCreate = () => {
        setCreateEntity({
            id: 1,
            nume: '',
            prenume: '',
            email: 'email@exemple.com',
            grad_didactic: '',
            tip_asociere: '',
            afiliere: '',
            links: {
                update: { href: '' },
                delete: { href: '' },
                self: { href: `${API_BASE_URL_M1}/api/academia/professors` },
                parent: { href: '' }
            }
        });
    };

    const toggleMenu = (id: number) => {
        setMenuOpen(prev => ({ ...prev, [id]: !prev[id] }));
    };

    const handleUpdateProfessor = (professor: Professor | ProfessorCreate) => {
        if ('links' in professor && 'id' in professor) {
            const updateLink = professor.links.update.href;
            const token = localStorage.getItem('token');
            if (!token) return;

            fetch(`${API_BASE_URL_M1}${updateLink}`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(professor),
            })
            .then(response => {
                if (response.ok) {
                    fetchProfessors();
                    setEditingEntity(null);
                } else {
                    console.error('Failed to update professor:', response.statusText);
                }
            })
            .catch(error => {
                console.error('Error updating professor:', error);
            });
        }
    };

    const handleDeleteProfessor = () => {
        if (deletingEntity) {
            const deleteLink = deletingEntity.links.delete.href;
            const token = localStorage.getItem('token');
            const professorEmail = deletingEntity.email;
            if (!token || !professorEmail) return;

            fetch(`${API_BASE_URL_M1}${deleteLink}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            })
            .then(async (response) => {
                if (response.ok) {
                    return fetch(`${API_BASE_URL_M3}?username=${professorEmail}`, { 
                        method: 'DELETE',
                        headers: {
                            'Authorization': `Bearer ${token}`,
                        },
                    });
                } else {
                    console.error('Failed to delete professor:', response.statusText);
                    throw new Error('Failed to delete professor');
                }
            })
            .then(async (userResponse) => {
                if (userResponse.ok) {
                    setDeletingEntity(null);
                    fetchProfessors(); 
                } else {
                    const text = await userResponse.text();
                    console.error('Failed to delete user:', userResponse.statusText, text);
                }
            })
            .catch(error => {
                console.error('Error deleting professor:', error);
            });
        }
    };

    const handleCreateNewProfessor = (professor: ProfessorCreate) => {
        const professorLink = `${API_BASE_URL_M1}/api/academia/professors`; 
        const token = localStorage.getItem('token');
        if (!token) return;

        const user: Omit<User, 'id' | 'links'> = {
            username: professor.email, 
            password: 'password', 
            role: 'profesor',
        };

        fetch(professorLink, { 
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(professor),
        })
        .then(async response => {
            if (response.ok) {

                const userLink = `${API_BASE_URL_M3}?role=${user.role}`;
                return fetch(userLink, { 
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(user),
                });
            } else {
                const text = await response.text();
                console.error('Failed to create professor:', response.statusText, text);
                throw new Error('Failed to create professor');
            }
        })
        .then(async userResponse => {
            if (userResponse.ok) {
                setCreateEntity(null); 
                fetchProfessors();
            } else {
                const text = await userResponse.text();
                console.error('Failed to create user:', userResponse.statusText, text);
            }
        })
        .catch(error => {
            console.error('Error creating professor or user:', error);
        });
    };
    
    useEffect(() => {
        fetchProfessors();
    }, [acadRank, affiliation, name, itemsPerPage, currentPage]);

    return (
        <div>
            <button onClick={fetchProfessors}>Show Professors</button>
            <button onClick={handleCreate}>Create Professor</button>
            <div style={{ display: 'flex', flexDirection: 'row',  }}>
                <label>Grad academic:</label>
                <select value={acadRank} onChange={(e) => { setAcadRank(e.target.value); handleFilterChange(); }}>
                    <option value="">Selecteaza</option>
                    <option value="asistent">Asistent</option>
                    <option value="sef_lucrari">Sef Lucrari</option>
                    <option value="conferentiar">Conferentiar</option>
                    <option value="profesor">Profesor</option>
                </select>

                <label>Afiliere:</label>
                <input type="text" value={affiliation} onChange={(e) => { setAffiliation(e.target.value); handleFilterChange(); }} />

                <label>Nume:</label>
                <input type="text" value={name} onChange={(e) => { setName(e.target.value); handleFilterChange(); }} />
            </div>
                        {professors.length > 0 && (
                        <div>
                            <table>
                                <thead>
                                    <tr>
                                        <th>Nume</th>
                                        <th>Prenume</th>
                                        <th>Email</th>
                                        <th>Grad Didactic</th>
                                        <th>Tip Asociere</th>
                                        <th>Afiliere</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {professors.map((professor) => (
                                        <tr key={professor.id}>
                                            <td>{professor.nume}</td>
                                            <td>{professor.prenume}</td>
                                            <td>{professor.email}</td>
                                            <td>{professor.grad_didactic}</td>
                                            <td>{professor.tip_asociere}</td>
                                            <td>{professor.afiliere}</td>
                                            <td>
                                                <button onClick={() => toggleMenu(professor.id)}>⋮</button>
                                                {menuOpen[professor.id] && (
                                                    <div className="menu">
                                                        <button onClick={() => handleEdit(professor)}>Edit</button>
                                                        <button onClick={() => handleDelete(professor)}>Delete</button>
                                                    </div>
                                                )}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>

                            <div>
                                <label htmlFor="itemsPerPage">Items per page:</label>
                                <select id="itemsPerPage" value={itemsPerPage} onChange={handleItemsPerPageChange}>
                                    <option value={1}>1</option>
                                    <option value={5}>5</option>
                                    <option value={10}>10</option>
                                    <option value={15}>15</option>
                                </select>
                            </div>
                            <div>
                                <p>Current Page: {currentPage}</p>
                                <button onClick={() => handlePageChange(currentPage - 1)} disabled={currentPage === 1}>Previous</button>
                                <button onClick={() => handlePageChange(currentPage + 1)}>Next</button>
                            
                            </div>
                        </div>
                    )}

                    {editingEntity && (
                        <EditFormProfessor
                            entity={editingEntity}
                            onSave={handleUpdateProfessor} 
                            onCancel={() => setEditingEntity(null)}
                            isEdit={true}
                        />
                    )}
                    {deletingEntity && (
                        <ConfirmDelete
                            onConfirm={handleDeleteProfessor} 
                            onCancel={() => setDeletingEntity(null)}
                        />
                    )}
                    {createEntity && (
                        <EditFormProfessor
                            entity={createEntity}
                            onSave={handleCreateNewProfessor} 
                            onCancel={() => setCreateEntity(null)}
                            isEdit={false}
                        />
                    )}
        </div>
    );
};

export default Professors;
