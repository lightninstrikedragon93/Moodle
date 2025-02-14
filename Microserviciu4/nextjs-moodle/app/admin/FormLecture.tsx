import React, { useState } from 'react';
import { Lecture, LectureCreate } from '../interfaces/lectures';

interface EditFormProps {
    entity: Lecture | LectureCreate; 
    onSave: (updatedEntity: Lecture | LectureCreate) => void;
    onCancel: () => void; 
}

const EditFormLecture: React.FC<EditFormProps> = ({ entity, onSave, onCancel }) => {
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
                <label>Cod:</label>
                <input type="text" name="cod" value={formData.cod} onChange={handleChange} required/>
            </div>
            <div>
                <label>ID Titular:</label>
                <input type="number" name="id_titular" value={formData.id_titular} onChange={handleChange} required/>
            </div>
            <div>
                <label>Nume:</label>
                <input type="text" name="nume_disciplina" value={formData.nume_disciplina} onChange={handleChange} required/>
            </div>
            <div>
                <label>An Studiu:</label>
                <select name="an_studiu" value={formData.an_studiu} onChange={handleChange} required>
                    <option value="">Selecteaza</option>
                    <option value={1}>1</option>
                    <option value={2}>2</option>
                    <option value={3}>3</option>
                    <option value={4}>4</option>
                </select>
            </div>
            <div>
                <label>Tip Disciplina:</label>
                <select name="tip_disciplina" value={formData.tip_disciplina} onChange={handleChange} required>
                    <option value="">Selecteaza </option>
                    <option value="impusa">Impusa</option>
                    <option value="optinala">Optionala</option>
                    <option value="liber_aleasa">Liber Aleasa</option>
                </select>
            </div>
            <div>
                <label>Categorie:</label>
                <select name="categorie_disciplina" value={formData.categorie_disciplina} onChange={handleChange} required>
                    <option value="">Selecteaza </option>
                    <option value="domeniu">Domeniu</option>
                    <option value="specialitate">Specialitate</option>
                    <option value="adiacenta">Adiacenta</option>
                </select>
            </div>
            <div>
                <label>Tip Examinare:</label>
                <select name="tip_examinare" value={formData.tip_examinare} onChange={handleChange} required>
                    <option value="">Selecteaza </option>
                    <option value="examen">Examen</option>
                    <option value="colocviu">Colocviu</option>
                </select>
            </div>
            <button type="submit">Save</button>
            <button type="button" onClick={onCancel}>Cancel</button>
        </form>
    );
};

export default EditFormLecture;