import client from './client';

export const authAPI = {
    login: async (email, password) => {
        const response = await client.post('/auth/login', { email, password });
        return response.data;
    },

    register: async (email, password, name) => {
        const response = await client.post('/auth/register', { email, password, name });
        return response.data;
    },

    getCurrentUser: async () => {
        const response = await client.get('/auth/me');
        return response.data;
    }
};
