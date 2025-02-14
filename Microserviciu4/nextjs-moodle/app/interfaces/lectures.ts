export interface LectureCreate {
    cod: string;
    id_titular: number;
    nume_disciplina: string;
    an_studiu: number;
    tip_disciplina: string;
    categorie_disciplina: string;
    tip_examinare: string;
}

export interface Lecture extends LectureCreate {
    links: {
        self: { href: string };   
        parent: { href: string }; 
        update: { href: string }; 
        delete: { href: string };
    };
}
