import React, { useState } from 'react';
import { Professor, ProfessorCreate } from '../interfaces/professor';

interface EditFormProps {
    entity: Professor | ProfessorCreate; 
    onSave: (updatedEntity: Professor | ProfessorCreate) => void;
    onCancel: () => void;
    isEdit: boolean;
}

const EditFormProfessor: React.FC<EditFormProps> = ({ entity, onSave, onCancel, isEdit}) => {
    const [formData, setFormData] = useState(entity);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
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
                <input type="text" name="nume" value={formData.nume} onChange={handleChange} required/>
            </div>
            <div>
                <label>Prenume:</label>
                <input type="text" name="prenume" value={formData.prenume} onChange={handleChange} required/>
            </div>
            <div>
                <label>Email:</label>
                <input type="text" name="email" value={formData.email} onChange={handleChange} required disabled={isEdit} />
            </div>
            <div>
                <label>Grad Didactic:</label>
                <select name="grad_didactic" value={formData.grad_didactic} onChange={handleChange} required>
                    <option value="">Selecteaza</option>
                    <option value="asistent">Asistent</option>
                    <option value="sef_lucrari">Sef Lucrari</option>
                    <option value="conferentiar">Conferentiar</option>
                    <option value="profesor">Profesor</option>
                </select>
            </div>
            <div>
                <label>Tip Asociere:</label>
                <select name="tip_asociere" value={formData.tip_asociere} onChange={handleChange} required>
                    <option value="">Selecteaza </option>
                    <option value="titular">Titular</option>
                    <option value="asociere">Asociere</option>
                    <option value="extern">Extern</option>
                </select>
            </div>
            <div>
                <label>Afiliere:</label>
                <input type="text" name="afiliere" value={formData.afiliere} onChange={handleChange} required/>
            </div>
            <button type="submit">Save</button>
            <button type="button" onClick={onCancel}>Cancel</button>
        </form>
    );
};

export default EditFormProfessor;