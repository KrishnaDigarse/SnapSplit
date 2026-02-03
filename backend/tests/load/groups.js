import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    vus: 10,
    duration: '30s',
};

const BASE_URL = 'http://localhost:8000/api/v1';

// Setup: Login to get token
export function setup() {
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
    return { token: res.json('access_token') };
}

export default function (data) {
    const headers = { 'Authorization': `Bearer ${data.token}` };

    const res = http.get(`${BASE_URL}/groups`, { headers: headers });

    check(res, {
        'status is 200': (r) => r.status === 200,
        'groups list returned': (r) => Array.isArray(r.json()),
    });

    sleep(1);
}
