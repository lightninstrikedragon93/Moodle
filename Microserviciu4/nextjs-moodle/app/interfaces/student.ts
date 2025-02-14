
export interface StudentCreate {
    nume: string;
    prenume: string;
    email: string;
    ciclu_studii: string;
    an_studii: number;
    grupa: number;
}

export interface Student extends StudentCreate {
    id: number;
    links: {
        [key: string]: {
            href: string;
        };
    };
}
