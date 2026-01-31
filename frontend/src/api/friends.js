import client from './client';

export const friendsAPI = {
    // Get friends list
    getFriends: async () => {
        const response = await client.get('/friends');
        return response.data;
    },

    // Send friend request
    sendFriendRequest: async (email) => {
        const response = await client.post('/friends/request', { friend_email: email });
        return response.data;
    },

    // Accept friend request
    acceptFriendRequest: async (requestId) => {
        const response = await client.post(`/friends/request/${requestId}/accept`);
        return response.data;
    },

    // Reject friend request
    rejectFriendRequest: async (requestId) => {
        const response = await client.post(`/friends/request/${requestId}/reject`);
        return response.data;
    },

    // Get pending friend requests
    getPendingRequests: async () => {
        const response = await client.get('/friends/requests');
        return response.data;
    }
};
