interface User{
    id: number;
    username: string;
    password: string;
    role: string;
    links: {
        update: { href: string };
        delete: { href: string };
        self: { href: string };
        parent: { href: string };
    };
}