export interface MaterialeCreate{
    titlu: string;
    continut: string;
    capitol: number;
    saptamana: number;
 
}

export interface Materiale extends MaterialeCreate {
    links: {
        self: { href: string };
        parent: { href: string };
        update: { href: string };
        delete: { href: string };
    };
}
    