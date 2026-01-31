import client from './client';

export const expensesAPI = {
    // Upload bill (async) - Returns HTTP 202
    uploadBill: async (groupId, imageFile) => {
        const formData = new FormData();
        formData.append('image', imageFile);
        formData.append('group_id', groupId);

        const response = await client.post('/expenses/bill', formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        return response.data;
    },

    // Poll expense status
    pollExpenseStatus: async (expenseId) => {
        const response = await client.get(`/expenses/${expenseId}/status`);
        return response.data;
    },

    // Get expense detail
    getExpenseDetail: async (expenseId) => {
        const response = await client.get(`/expenses/${expenseId}`);
        return response.data;
    },

    // Create manual expense
    createManualExpense: async (data) => {
        const response = await client.post('/expenses', data);
        return response.data;
    },

    // Get expenses for a group
    getGroupExpenses: async (groupId) => {
        const response = await client.get(`/groups/${groupId}/expenses`);
        return response.data;
    }
};
