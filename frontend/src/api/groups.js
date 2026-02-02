import client from './client';

export const groupsAPI = {
    // Get all groups (exclude DIRECT)
    getGroups: async () => {
        const response = await client.get('/groups');
        return response.data;
    },

    // Get group detail
    getGroupDetail: async (groupId) => {
        const response = await client.get(`/groups/${groupId}`);
        return response.data;
    },

    // Create group
    createGroup: async (groupData) => {
        const response = await client.post('/groups', groupData);
        return response.data;
    },

    // Record a settlement payment
    recordSettlement: async (settlementData) => {
        const response = await client.post('/settlements', settlementData);
        return response.data;
    },

    // Delete group
    deleteGroup: async (groupId) => {
        const response = await client.delete(`/groups/${groupId}`);
        return response.data;
    },

    // Add member to group
    addMember: async (groupId, userId) => {
        const response = await client.post(`/groups/${groupId}/add-member`, { user_id: userId });
        return response.data;
    },

    // Remove member from group
    removeMember: async (groupId, userId) => {
        const response = await client.delete(`/groups/${groupId}/members/${userId}`);
        return response.data;
    },

    // Get group balances
    getGroupBalances: async (groupId) => {
        const response = await client.get(`/groups/${groupId}/balances`);
        return response.data;
    },

    // Leave group
    leaveGroup: async (groupId) => {
        const response = await client.post(`/groups/${groupId}/leave`);
        return response.data;
    }
};
