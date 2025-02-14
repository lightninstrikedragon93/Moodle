export interface ProfessorCreate {
    nume: string;
    prenume: string;
    email: string;
    grad_didactic: string;
    tip_asociere: string;
    afiliere: string;
}

export interface Professor extends ProfessorCreate {
    id: number;
    links: {
        self: { href: string };
        parent: { href: string };
        update: { href: string };
        delete: { href: string };
    };
}
