import React, { useState } from 'react';
import { Student } from '../interfaces/student';
import { StudentCreate } from '../interfaces/student';

interface EditFormProps {
    entity: Student | StudentCreate;
    onSave: (updatedEntity: Student | StudentCreate) => void;
    onCancel: () => void;
    isEdit: boolean;
}

const EditFormStudent: React.FC<EditFormProps> = ({ entity, onSave, onCancel,  isEdit }) => {
    const [formData, setFormData] = useState(entity);

    const handleChange = (e: React.ChangeEvent<HTMLSelectElement | HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData({ ...formData, [name]: value });
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSave(formData);
    };

    return (
        <form onSubmit={handleSubmit}>
            <div>
                <label>Nume:</label>
                <input type="text" name="nume" value={formData.nume} onChange={handleChange} required />
            </div>
            <div>
                <label>Prenume:</label>
                <input type="text" name="prenume" value={formData.prenume} onChange={handleChange} required />
            </div>
            <div>
                <label>Email:</label>
                <input type="text" name="email" value={formData.email} onChange={handleChange} required disabled={isEdit}/>
            </div>
            <div>
                <label>Ciclu Studii:</label>
                <select name="ciclu_studii" value={formData.ciclu_studii} onChange={handleChange} required>
                    <option value="">Selecteaza</option>
                    <option value="licenta">Licenta</option>
                    <option value="master">Master</option>
                </select>
            </div>
            <div>
                <label>An Studiu:</label>
                <input type="number" name="an_studii" value={formData.an_studii} onChange={handleChange} required/>
            </div>
            <div>
                <label>Grupa:</label>
                <input type="number" name="grupa" value={formData.grupa} onChange={handleChange} required/>
            </div>
            <button type="submit">Save</button>
            <button type="button" onClick={onCancel}>Cancel</button>
        </form>
    );
};

export default EditFormStudent;