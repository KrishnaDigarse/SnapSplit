import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { groupsAPI } from '../api/groups';
import { expensesAPI } from '../api/expenses';
import { Layout } from '../components/layout/Layout';
import { BillUpload } from '../components/expense/BillUpload';
import { Spinner } from '../components/common/Spinner';
import { Button } from '../components/common/Button';
import { Link } from 'react-router-dom';

export const GroupDetail = () => {
    const { groupId } = useParams();

    const { data: group, isLoading: groupLoading } = useQuery({
        queryKey: ['groups', groupId],
        queryFn: () => groupsAPI.getGroupDetail(groupId)
    });

    const { data: expenses, isLoading: expensesLoading } = useQuery({
        queryKey: ['expenses', groupId],
        queryFn: () => expensesAPI.getGroupExpenses(groupId)
    });

    const { data: balances } = useQuery({
        queryKey: ['balances', groupId],
        queryFn: () => groupsAPI.getGroupBalances(groupId)
    });

    if (groupLoading) {
        return (
            <Layout>
                <div className="text-center py-12">
                    <Spinner size="lg" />
                </div>
            </Layout>
        );
    }

    return (
        <Layout>
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900">{group?.name}</h1>
                <p className="mt-2 text-gray-600">{group?.members?.length || 0} members</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
                <div className="lg:col-span-2">
                    <BillUpload groupId={groupId} />
                </div>

                <div className="bg-white p-6 rounded-lg shadow">
                    <h3 className="text-lg font-semibold mb-4">Group Members</h3>
                    {group?.members && group.members.length > 0 ? (
                        <div className="space-y-3">
                            {group.members.map((member) => (
                                <div key={member.id} className="flex items-center">
                                    <div className="flex-shrink-0">
                                        <div className="h-8 w-8 rounded-full bg-primary-100 flex items-center justify-center">
                                            <span className="text-primary-600 font-medium text-sm">
                                                {member.name?.charAt(0).toUpperCase() || 'U'}
                                            </span>
                                        </div>
                                    </div>
                                    <div className="ml-3">
                                        <p className="text-sm font-medium text-gray-900">{member.name}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="text-sm text-gray-600">No members yet</p>
                    )}
                </div>
            </div>

            {balances && balances.length > 0 && (
                <div className="bg-white rounded-lg shadow mb-8">
                    <div className="px-6 py-4 border-b">
                        <h2 className="text-xl font-semibold text-gray-900">Balances</h2>
                    </div>
                    <div className="p-6">
                        <div className="space-y-3">
                            {balances.map((balance, idx) => (
                                <div key={idx} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                                    <span className="text-sm text-gray-700">
                                        {balance.from_user} owes {balance.to_user}
                                    </span>
                                    <span className="font-semibold text-gray-900">
                                        ₹{balance.amount}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            <div className="bg-white rounded-lg shadow">
                <div className="px-6 py-4 border-b">
                    <h2 className="text-xl font-semibold text-gray-900">Expenses</h2>
                </div>
                {expensesLoading ? (
                    <div className="p-12 text-center">
                        <Spinner />
                    </div>
                ) : expenses && expenses.length > 0 ? (
                    <div className="divide-y">
                        {expenses.map((expense) => (
                            <Link
                                key={expense.id}
                                to={`/expenses/${expense.id}`}
                                className="block p-6 hover:bg-gray-50 transition-colors"
                            >
                                <div className="flex justify-between items-start">
                                    <div className="flex-1">
                                        <div className="flex items-center space-x-2">
                                            <h3 className="font-medium text-gray-900">
                                                {expense.description || 'Expense'}
                                            </h3>
                                            <span className={`px-2 py-1 text-xs rounded-full ${expense.status === 'READY' ? 'bg-green-100 text-green-800' :
                                                    expense.status === 'PROCESSING' ? 'bg-yellow-100 text-yellow-800' :
                                                        expense.status === 'FAILED' ? 'bg-red-100 text-red-800' :
                                                            'bg-gray-100 text-gray-800'
                                                }`}>
                                                {expense.status}
                                            </span>
                                            {expense.source_type === 'BILL_IMAGE' && (
                                                <span className="text-xs text-primary-600">🤖 AI</span>
                                            )}
                                        </div>
                                        <p className="text-sm text-gray-600 mt-1">
                                            {new Date(expense.created_at).toLocaleDateString()}
                                        </p>
                                    </div>
                                    <div className="text-right">
                                        <p className="font-semibold text-gray-900">
                                            ₹{expense.total_amount || '0.00'}
                                        </p>
                                        {expense.items && (
                                            <p className="text-sm text-gray-600">{expense.items.length} items</p>
                                        )}
                                    </div>
                                </div>
                            </Link>
                        ))}
                    </div>
                ) : (
                    <div className="p-12 text-center">
                        <p className="text-gray-600">No expenses yet. Upload a bill to get started!</p>
                    </div>
                )}
            </div>
        </Layout>
    );
};
