import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    vus: 5,
    duration: '30s',
};

const BASE_URL = 'http://localhost:8000/api/v1';
const GROUP_ID = '4bf3a832-3070-4fff-8da3-715e1aa0411d'; // Real group ID (Postgres)
const USER_ID = '23e1f129-90a7-409b-a75d-7197485c6733'; // Real User ID (Postgres)

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
    const headers = {
        'Authorization': `Bearer ${data.token}`,
        'Content-Type': 'application/json'
    };

    const payload = JSON.stringify({
        group_id: GROUP_ID,
        description: 'Load Test Expense',
        items: [{ item_name: 'Load Test Item', price: 100, quantity: 1 }],
        splits: [{ user_id: USER_ID, amount: 100 }],
        subtotal: 100,
        tax: 0,
        total_amount: 100
    });

    // Note: Creating manual expense
    const res = http.post(`${BASE_URL}/expenses/manual`, payload, { headers: headers });

    check(res, {
        'status is 201': (r) => r.status === 201,
    });

    sleep(1);
}
