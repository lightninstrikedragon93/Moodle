import { useEffect, useState } from "react";
import { Lecture, LectureCreate } from '../interfaces/lectures';
import EditFormLecture from "./FormLecture";
import ConfirmDelete from "./confirmDelete";

const API_BASE_URL_M1 = 'http://localhost:8000';

const Lectures: React.FC = () => {
    const [currentPage, setCurrentPage] = useState<number>(1);
    const [itemsPerPage, setItemsPerPage] = useState<number>(5);
    const [menuOpen, setMenuOpen] = useState<{ [key: string]: boolean }>({});
    const [lectures, setLectures] = useState<Lecture []>([]);
    const [editingEntity, setEditingEntity] = useState<Lecture | null>(null);
    const [deletingEntity, setDeletingEntity] = useState<Lecture | null>(null);
    const [createEntity, setCreateEntity] = useState<LectureCreate | null>(null);

    const fetchLectures = async () => {
        const token = localStorage.getItem('token');
        if (!token) return;

        const response = await fetch(`${API_BASE_URL_M1}/api/academia/lectures/?skip=${(currentPage - 1) * itemsPerPage}&limit=${itemsPerPage}`, {
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

    const handleEdit = (lecture: Lecture) => {
        setEditingEntity(lecture); 
    };

    const handleDelete = (student: Lecture) => {
        setDeletingEntity(student);
    };
    const handleCreate = () => {
        setCreateEntity({
            cod: '',
            id_titular: 1,
            nume_disciplina: '',
            an_studiu: 1,
            tip_disciplina: '',
            categorie_disciplina: '',
            tip_examinare: '',
        });
    };
    const handlePageChange = (page: number) => {
        setCurrentPage(page);
        fetchLectures();       

    };

    const handleItemsPerPageChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        const newValue = Number(event.target.value)
        setItemsPerPage(newValue);
        setCurrentPage(1);   
    };

    const toggleMenu = (lecture: Lecture) => {
        setMenuOpen(prev => ({ ...prev, [lecture.cod]: !prev[lecture.cod] }));
    };

    const handleCreateNewLecture = (lecture: LectureCreate) => {
        const lectureLink = `${API_BASE_URL_M1}/api/academia/lectures`
        const token = localStorage.getItem('token');
        if (!token) return;

        fetch(lectureLink, { 
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(lecture),
        })
        .then(async response => {
            if (response.ok) {
                setCreateEntity(null);
                fetchLectures();
            } else {
                const text = await response.text();
                console.error('Failed to create lecture:', response.statusText, text);
                throw new Error('Failed to create lecture');
            }
        })
        
        .catch(error => {
            console.error('Error creating lecture:', error);
        });
        console.log(lecture);
    }

    const handleUpdateLecture = (lecture: Lecture | LectureCreate) => {
        if ('links' in lecture) {
            const updateLink = lecture.links.update.href;
            const token = localStorage.getItem('token');
            if (!token) return;
    
            const {links, ...dataToUpdate } = lecture;
    
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
                    setEditingEntity(null);
                    fetchLectures();
                } else {
                    console.error('Failed to update lecture:', response.statusText);
                }
            })
            .catch(error => {
                console.error('Error updating lecture:', error);
            });
        } else {
            console.error('Invalid lecture object for update');
        }
    };

    const handleDeleteLecture = () => {
        if (deletingEntity) {
            const deleteLink = deletingEntity.links.delete.href;
            const token = localStorage.getItem('token');
            if (!token) return;

            fetch(`${API_BASE_URL_M1}${deleteLink}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            })
            .then(response => {
                if (response.ok) {
                    setDeletingEntity(null);
                    fetchLectures();
                } else {
                    console.error('Failed to delete lecture:', response.statusText);
                }
            })
            .catch(error => {
                console.error('Error deleting lecture:', error);
            });
        }
    };

    useEffect(() => {
        fetchLectures();
    }, [itemsPerPage, currentPage]);
    return (
        <div>
            <button onClick={fetchLectures}>Show Lectures</button>
            <button onClick={handleCreate}>Create Lecture</button>
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
                                                    <button onClick={() => handleEdit(lecture)}>Edit</button>
                                                    <button onClick={() => handleDelete(lecture)}>Delete</button>
                                                
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

                    

                    {editingEntity && (
                    <EditFormLecture
                        entity={editingEntity}
                        onSave={handleUpdateLecture} 
                        onCancel={() => setEditingEntity(null)} 
                    />)}
                    {deletingEntity && (
                        <ConfirmDelete
                            onConfirm={handleDeleteLecture} 
                            onCancel={() => setDeletingEntity(null)}
                        />
                    )}
                    {createEntity && (
                    <EditFormLecture
                        entity={createEntity}
                        onSave={handleCreateNewLecture} 
                        onCancel={() => setCreateEntity(null)}
                    />)}
                </div>
            )}
        </div>
    );
};

export default Lectures;