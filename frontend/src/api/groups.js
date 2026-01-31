import client from './client';

export const groupsAPI = {
    // Get all groups (exclude DIRECT)
    getGroups: async () => {
        const response = await client.get('/groups');
        return response.data.filter(group => group.type !== 'DIRECT');
    },

    // Create group
    createGroup: async (name, type = 'CUSTOM') => {
        const response = await client.post('/groups', { name, type });
        return response.data;
    },

    // Get group detail
    getGroupDetail: async (groupId) => {
        const response = await client.get(`/groups/${groupId}`);
        return response.data;
    },

    // Add member to group
    addMemberToGroup: async (groupId, userId) => {
        const response = await client.post(`/groups/${groupId}/members`, { user_id: userId });
        return response.data;
    },

    // Get group balances
    getGroupBalances: async (groupId) => {
        const response = await client.get(`/groups/${groupId}/balances`);
        return response.data;
    }
};
