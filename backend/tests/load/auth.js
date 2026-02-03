import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    stages: [
        { duration: '30s', target: 20 },
        { duration: '1m', target: 20 },
        { duration: '10s', target: 0 },
    ],
};

const BASE_URL = 'http://localhost:8000/api/v1';

export default function () {
    const payload = JSON.stringify({
        email: 'krishna@example.com',
        password: 'password123',
    });

    const params = {
        headers: {
            'Content-Type': 'application/json',
        },
    };

    const res = http.post(`${BASE_URL}/auth/login`, payload, params);

    check(res, {
        'status is 200': (r) => r.status === 200,
        'token present': (r) => r.json('access_token') !== undefined,
    });

    sleep(1);
}
