import React, { useEffect, useState } from 'react';
import { Materiale, MaterialeCreate} from '../interfaces/materiale';

interface EditFormProps {
    entity: Materiale | MaterialeCreate; 
    onSave: (updatedEntity: Materiale | MaterialeCreate) => void;
    onCancel: () => void; 
}

const EditFormMateriale: React.FC<EditFormProps> = ({ entity, onSave, onCancel }) => {
    const [formData, setFormData] = useState(entity);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        //console.log("Entity: ", entity);
        setFormData({ ...formData, [name]: value });
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSave(formData);
    };
    
    return (
        <form onSubmit={handleSubmit}>
            <div>
                <label>Titlu:</label>
                <input type="text" name="titlu" value={formData.titlu} onChange={handleChange} required/>
            </div>
            <div>
                <label>Capitol:</label>
                <input type="number" name="capitol" value={formData.capitol} onChange={handleChange} required/>
            </div>
            <div>
                <label>Saptamana:</label>
                <input type="number" name="saptamana" value={formData.saptamana} onChange={handleChange} required/>
            </div>
            <div>
                <label>Continut:</label>
                <input type="text" name="continut" value={formData.continut} onChange={handleChange} required/>
            </div>
            <button type="submit">Save</button>
            <button type="button" onClick={onCancel}>Cancel</button>
        </form>
    );
};

export default EditFormMateriale;