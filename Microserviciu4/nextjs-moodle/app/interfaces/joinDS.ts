export interface JoinDSCreate {
    student_id: number;
    disciplina_cod: string;
}
export interface JoinDS extends JoinDSCreate {
    links: {
        self: { href: string };  
        parent: { href: string }; 
        update: { href: string }; 
        delete: { href: string }; 
    };
}
