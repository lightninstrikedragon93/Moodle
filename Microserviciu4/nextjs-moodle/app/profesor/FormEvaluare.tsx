import React, { useState } from 'react';
import { Evaluation, EvaluationCreate } from '../interfaces/evaluation';

interface EditFormProps {
    entity: Evaluation | EvaluationCreate;
    onSave: (updatedEntity: Evaluation | EvaluationCreate ) => void;
    onCancel: () => void;
}

const EditFormEvaluare: React.FC<EditFormProps> = ({ entity, onSave, onCancel }) => {
    const [formData, setFormData] = useState(entity);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        console.log("Form data on change: ",formData)
        setFormData((prevState) => ({ ...prevState, [name]: value }));
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        console.log("Form data on submit: ",formData)
        onSave(formData);
    };

    return (
        <form onSubmit={handleSubmit}>
            <div>
                <label>Tip:</label>
                <input type="text" name="tip" value={formData.tip} onChange={handleChange} required />
            </div>
            <div>
                <label>Pondere:</label>
                <input type="number" name="pondere" value={formData.pondere} onChange={handleChange} required />
            </div>
            <button type="submit">Save</button>
            <button type="button" onClick={onCancel}>Cancel</button>
        </form>
    );
};

export default EditFormEvaluare;