interface AppData {
    Name: string;
    OS: 'iOS' | 'Android';
    Tag: string;
    Rating: number | 'N/A';
    Downloads: number | 'N/A';
    Reviews: number | 'N/A';
    Country: string;
    Release_date: string | 'N/A';
    Developer: string;
    link: string;
    devLink: string | 'N/A';
    id: string;
}

interface AppReview {
    user: string;
    review: string;
    rating: number;
    date: string;
}
