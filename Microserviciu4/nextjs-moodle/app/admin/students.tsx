import React, { useEffect, useState } from 'react';
import EditFormStudent from './FormStudent';
import ConfirmDelete from './confirmDelete';
import { Student, StudentCreate } from '../interfaces/student';
import { JoinDS, JoinDSCreate } from '../interfaces/joinDS';
import { Lecture } from '../interfaces/lectures';

const API_BASE_URL_M1 = 'http://localhost:8000';
const API_BASE_URL_M3 = 'http://localhost:8002/api/academia_user';


const Students: React.FC = () => {
    const [students, setStudents] = useState<any[]>([]);
    const [currentPage, setCurrentPage] = useState<number>(1);
    const [itemsPerPage, setItemsPerPage] = useState<number>(5);
    const [menuOpen, setMenuOpen] = useState<{ [key: number]: boolean }>({});
    const [editingEntity, setEditingEntity] = useState<Student | null>(null);
    const [deletingEntity, setDeletingEntity] = useState<Student | null>(null);
    const [createEntity, setCreateEntity] = useState<StudentCreate | null>(null);
    const [lectures, setLectures] = useState<Lecture []>([]);
    const [selectedStudent, setSelectedStudent] = useState<Student | null>(null);
    const [createJoinDS, setCreateJoinDS] = useState<JoinDS | null>(null);
    const [associationStatus, setAssociationStatus] = useState<{ [key: string]: boolean }>({});

    const fetchStudents = async () => {
        const token = localStorage.getItem('token');
        if (!token) return;

        try {
            const response = await fetch(`${API_BASE_URL_M1}/api/academia/all_students?skip=${(currentPage - 1) * itemsPerPage}&limit=${itemsPerPage}`, {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            });

            if (response.ok) {
                const data = await response.json();
                setStudents(data);
            } else {
                console.error('Failed to fetch students:', response.statusText);
            }
        } catch (error) {
            console.error('Error fetching students:', error);
        }
    };

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


    const handlePageChange = (page: number) => {
        setCurrentPage(page);
        fetchStudents();       

    };

    const handleItemsPerPageChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        const newValue = Number(event.target.value)
        setItemsPerPage(newValue);
        setCurrentPage(1);   
    };

    const handleEdit = (student: Student) => {
        setEditingEntity(student); 
    };

    const handleDelete = (student: Student) => {
        setDeletingEntity(student);
    };
    const handleCreate = () => {
        setCreateEntity({
            nume: '',
            prenume: '',
            email: 'email@exemple.com',
            an_studii: 1,
            ciclu_studii: '',
            grupa: 1
        });
    };

    const handleUpdateStudent = (student: Student | StudentCreate) => {
        if ('links' in student && 'id' in student) {
            const updateLink = student.links.update.href;
            const token = localStorage.getItem('token');
            if (!token) return;
    
            const { id, links, ...dataToUpdate } = student;
    
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
                    fetchStudents();
                } else {
                    console.error('Failed to update student:', response.statusText);
                }
            })
            .catch(error => {
                console.error('Error updating student:', error);
            });
        } else {
            console.error('Invalid student object for update');
        }
    };

    const handleDeleteStudent = () => {
        if (deletingEntity) {
            const deleteLink = deletingEntity.links.delete.href;
            const studentEmail = deletingEntity.email;
            const token = localStorage.getItem('token');
            if (!token || !studentEmail) return;

            fetch(`${API_BASE_URL_M1}${deleteLink}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${token}`,
                },
            })
            .then(async (response) => {
                if (response.ok) {
                    return fetch(`${API_BASE_URL_M3}?username=${studentEmail}`, { 
                        method: 'DELETE',
                        headers: {
                            'Authorization': `Bearer ${token}`,
                        },
                    });
                } else {
                    console.error('Failed to delete student:', response.statusText);
                    throw new Error('Failed to delete student');
                }
            })
            .then(async (userResponse) => {
                if (userResponse.ok) {
                    setDeletingEntity(null);
                    fetchStudents(); 
                } else {
                    const text = await userResponse.text();
                    console.error('Failed to delete user:', userResponse.statusText, text);
                }
            })
            .catch((error) => {
                console.error('Error deleting student and user:', error);
            });
        }
    };

    const toggleMenu = (student: Student) => {
        setMenuOpen(prev => ({ ...prev, [student.id]: !prev[student.id] }));
    };

    useEffect(() => {
        fetchStudents();
        fetchLectures();
    
        if (selectedStudent && lectures.length > 0) {
            lectures.forEach(lecture => {
                checkAssociation(selectedStudent.id, lecture.cod);
            });
        }
        
    }, [itemsPerPage, currentPage]);

    const handleCreateNewStudent = (student: StudentCreate) => {
        const studentLink = `${API_BASE_URL_M1}/api/academia/students`
        const token = localStorage.getItem('token');
        if (!token) return;

        const user: Omit<User, 'id' | 'links'> & { role: string } = {
            username: student.email,
            password: 'password',
            role: 'student',
        };

        fetch(studentLink, { 
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(student),
        })
        .then(async response => {
            if (response.ok) {
                return fetch(`${API_BASE_URL_M3}?role=${user.role}`, { 
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(user),
                });
            } else {
                const text = await response.text();
                console.error('Failed to create student:', response.statusText, text);
                throw new Error('Failed to create student');
            }
        })
        .then(async userResponse => {
            if (userResponse.ok) {
                setCreateEntity(null);
                fetchStudents();
            } else {
                const text = await userResponse.text();
                console.error('Failed to create user:', userResponse.statusText, text);
            }
        })
        .catch(error => {
            console.error('Error creating student:', error);
        });
    }


    const checkAssociation = async (studentId: number, lectureCode: string) => {
        const token = localStorage.getItem('token');
        const url = `${API_BASE_URL_M1}/api/academia/students/${studentId}/lectures/${lectureCode}/check`;
        try {
            const response = await fetch(url, {
                method: 'GET',
                headers: { 'Authorization': `Bearer ${token}` },
            });
            const data = await response.json();
            setAssociationStatus(prev => ({ ...prev, [`${studentId}-${lectureCode}`]: data.associated }));
        } catch (error) {
            console.error('Error checking association:', error);
        }
    };

    const handleCreateJoinDS = async (joinData: JoinDSCreate) => {
        const token = localStorage.getItem('token');
        const joinDSLinks = `${API_BASE_URL_M1}/api/academia/students/${joinData.student_id}/lectures?cod=${joinData.disciplina_cod}`;
        if (!token) return;

        fetch(joinDSLinks, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(joinData)
        })
        .then(async response =>{
            if(response.ok){
                setCreateJoinDS(null);
            }
            else{
                const text = await response.text();
                console.error('Failed to create association:', response.statusText, text);
            }
        })
        .catch(error => {
            console.error('Error creating association:', error);
        });
    };

    const handleDeleteJoinDS = async (joinData: JoinDS) => {
        const token = localStorage.getItem('token');
        const joinDSLinks = joinData.links.delete.href;
        console.log(joinDSLinks);
        const response = await fetch(joinData.links.delete.href, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`,
            }
        });

        if (response.ok) {
            console.log('Association deleted successfully');
        } else {
            console.error('Failed to delete association');
        }
        setCreateJoinDS(null);
    };


    const handleButtonClick = async (studentId: number, lectureCode: string) => {
        const isAssociated = associationStatus[`${studentId}-${lectureCode}`];
        const joinData: JoinDS = {
            student_id: studentId,
            disciplina_cod: lectureCode,
            links: {
                self: { href: `${API_BASE_URL_M1}/api/academia/students/${studentId}/lectures?cod=${lectureCode}` },
                parent: { href: `${API_BASE_URL_M1}/api/academia/students/${studentId}` },
                update: { href: '' }, 
                delete: { href: `${API_BASE_URL_M1}/api/academia/students/${studentId}/lectures/${lectureCode}` }
            }
        };

        if (isAssociated) {
            await handleDeleteJoinDS(joinData);
            setAssociationStatus(prev => ({ ...prev, [`${studentId}-${lectureCode}`]: false }));
        } else {
            await handleCreateJoinDS(joinData);
            setAssociationStatus(prev => ({ ...prev, [`${studentId}-${lectureCode}`]: true }));
        }
    };
    

    return (
        <div>
            <button onClick={fetchStudents}>Show Students</button>
            <button onClick={handleCreate}>Create Student</button>
                {students.length > 0 && (
                <div>
                    <table>
                        <thead>
                            <tr>
                                <th>Nume</th>
                                <th>Prenume</th>
                                <th>Email</th>
                                <th>An de studii</th>
                                <th>Ciclul de studii</th>
                                <th>Grupa</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            {students.map((student) => (
                                <tr key={student.id}>
                                    <td>{student.nume}</td>
                                    <td>{student.prenume}</td>
                                    <td>{student.email}</td>
                                    <td>{student.an_studii}</td>
                                    <td>{student.ciclu_studii}</td>
                                    <td>{student.grupa}</td>
                                    <td>
                                        <button onClick={() => toggleMenu(student)}>⋮</button>
                                            {menuOpen[student.id] && (
                                                <div className="menu">
                                                    <button onClick={() => handleEdit(student)}>Edit</button>
                                                    <button onClick={() => handleDelete(student)}>Delete</button>
                                                    <button onClick={() => setSelectedStudent(student)}>Add Lecture</button>
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
                    <EditFormStudent
                        entity={editingEntity}
                        onSave={handleUpdateStudent} 
                        onCancel={() => setEditingEntity(null)}
                        isEdit={true} 
                    />
                )}
                {deletingEntity && (
                    <ConfirmDelete
                        onConfirm={handleDeleteStudent} 
                        onCancel={() => setDeletingEntity(null)}
                    />
                )}
                {createEntity && (
                <EditFormStudent
                    entity={createEntity}
                    onSave={handleCreateNewStudent} 
                    onCancel={() => setCreateEntity(null)}
                    isEdit={false} 
                />)}
                {lectures.length > 0 && selectedStudent && (
                <table>
                    <thead>
                        <tr>
                            <th>Discipline Name</th>
                            <th>Year of Study</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {lectures.map((lecture) => (
                            <tr key={lecture.cod}>
                                <td>{lecture.nume_disciplina}</td>
                                <td>{lecture.an_studiu}</td>
                                <td>
                                <button onClick={() => handleButtonClick(selectedStudent.id, lecture.cod)}>
                                    {associationStatus[`${selectedStudent.id}-${lecture.cod}`] ? 'Delete' : 'Associate'}
                                </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                )}
            </div>
        )}

        </div>
    
    );
};

export default Students;
