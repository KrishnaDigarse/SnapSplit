import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { groupsAPI } from '../api/groups';
import { Layout } from '../components/layout/Layout';
import { ManualExpenseForm } from '../components/expense/ManualExpenseForm';
import { Spinner } from '../components/common/Spinner';

export const ManualExpense = () => {
    const { groupId } = useParams();
    const navigate = useNavigate();

    const { data: group, isLoading } = useQuery({
        queryKey: ['groups', groupId],
        queryFn: () => groupsAPI.getGroupDetail(groupId)
    });

    if (isLoading) {
        return (
            <Layout>
                <div className="flex justify-center py-12">
                    <Spinner size="lg" />
                </div>
            </Layout>
        );
    }

    if (!group) {
        return (
            <Layout>
                <div className="text-center py-12">
                    <p className="text-red-600">Group not found</p>
                    <button onClick={() => navigate('/groups')} className="text-primary-600 underline mt-4">
                        Back to Groups
                    </button>
                </div>
            </Layout>
        );
    }

    return (
        <Layout>
            <div className="max-w-2xl mx-auto">
                <div className="mb-6">
                    <button
                        onClick={() => navigate(`/groups/${groupId}`)}
                        className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 mb-2 flex items-center"
                    >
                        ← Back to Group
                    </button>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                        Add Expense to {group.name}
                    </h1>
                </div>

                <ManualExpenseForm
                    groupId={groupId}
                    members={group.members || []}
                    onSuccess={() => navigate(`/groups/${groupId}`)}
                    onCancel={() => navigate(`/groups/${groupId}`)}
                />
            </div>
        </Layout>
    );
};
