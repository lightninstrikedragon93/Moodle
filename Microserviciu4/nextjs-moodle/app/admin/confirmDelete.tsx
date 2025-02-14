import React from 'react';

interface ConfirmDeleteProps {
    onConfirm: () => void;
    onCancel: () => void; 
}

const ConfirmDelete: React.FC<ConfirmDeleteProps> = ({ onConfirm, onCancel }) => {
    return (
        <div className="confirm-delete">
            <p>Are you sure you want to delete this item?</p>
            <button onClick={onConfirm}>Delete</button>
            <button onClick={onCancel}>Cancel</button>
        </div>
    );
};

export default ConfirmDelete;
