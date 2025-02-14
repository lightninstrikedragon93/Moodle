export interface EvaluationCreate{
    tip: string;
    pondere: number;
}

export interface Evaluation extends EvaluationCreate{
    links: {
        self: { href: string };
        parent: { href: string };
        update: { href: string };
        delete: { href: string };
    };
}