import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { groupsAPI } from '../api/groups';
import { expensesAPI } from '../api/expenses';
import { Layout } from '../components/layout/Layout';
import { BillUpload } from '../components/expense/BillUpload';
import { Spinner } from '../components/common/Spinner';
import { Button } from '../components/common/Button';
import { ConfirmDialog } from '../components/common/ConfirmDialog';
import { AddMemberModal } from '../components/group/AddMemberModal';
import { SettlementModal } from '../components/settlement/SettlementModal';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const GroupDetail = () => {
    const { groupId } = useParams();
    const navigate = useNavigate();
    const { user } = useAuth();
    const queryClient = useQueryClient();

    const [showAddMember, setShowAddMember] = useState(false);
    const [showDeleteGroup, setShowDeleteGroup] = useState(false);
    const [showLeaveGroup, setShowLeaveGroup] = useState(false);
    const [showSettlementModal, setShowSettlementModal] = useState(false);
    const [memberToRemove, setMemberToRemove] = useState(null);

    const { data: group, isLoading: groupLoading } = useQuery({
        queryKey: ['groups', groupId],
        queryFn: () => groupsAPI.getGroupDetail(groupId)
    });

    const { data: expenses, isLoading: expensesLoading } = useQuery({
        queryKey: ['expenses', groupId],
        queryFn: () => expensesAPI.getGroupExpenses(groupId)
    });

    const { data: balanceData } = useQuery({
        queryKey: ['balances', groupId],
        queryFn: () => groupsAPI.getGroupBalances(groupId)
    });

    const balances = balanceData?.balances || [];
    const debts = balanceData?.debts || [];

    const deleteGroupMutation = useMutation({
        mutationFn: () => groupsAPI.deleteGroup(groupId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['groups'] });
            navigate('/groups');
        }
    });

    const leaveGroupMutation = useMutation({
        mutationFn: () => groupsAPI.leaveGroup(groupId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['groups'] });
            navigate('/groups');
        }
    });

    const removeMemberMutation = useMutation({
        mutationFn: (userId) => groupsAPI.removeMember(groupId, userId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['groups', groupId] });
            setMemberToRemove(null);
        }
    });

    const handleDeleteGroup = () => {
        deleteGroupMutation.mutate();
    };

    const handleLeaveGroup = () => {
        leaveGroupMutation.mutate();
    };

    const handleRemoveMember = () => {
        if (memberToRemove) {
            removeMemberMutation.mutate(memberToRemove.user_id);
        }
    };

    const isCreator = group?.created_by === user?.id;
    const isDirect = group?.type === 'DIRECT';

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
            <div className="mb-8 flex justify-between items-start">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white">{group?.name}</h1>
                    <p className="mt-2 text-gray-600 dark:text-gray-400">{group?.members?.length || 0} members</p>
                </div>
                <div className="flex space-x-2">
                    {/* Add Expense Button - For everyone */}
                    <Button
                        onClick={() => navigate(`/groups/${groupId}/expense/manual`)}
                    >
                        + Add Expense
                    </Button>

                    <Button
                        variant="secondary"
                        onClick={() => setShowSettlementModal(true)}
                    >
                        Settle Up
                    </Button>

                    {/* Only show Add Member if Creator and NOT a DIRECT group */}
                    {isCreator && !isDirect && (
                        <Button
                            variant="secondary"
                            onClick={() => setShowAddMember(true)}
                        >
                            + Add Member
                        </Button>
                    )}

                    {/* Show Leave Group if NOT Creator and NOT a DIRECT group */}
                    {!isCreator && !isDirect && (
                        <Button
                            variant="secondary"
                            onClick={() => setShowLeaveGroup(true)}
                            className="text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20"
                        >
                            Leave Group
                        </Button>
                    )}

                    {/* Only show Delete Group if Creator and NOT a DIRECT group */}
                    {isCreator && !isDirect && (
                        <Button
                            variant="secondary"
                            onClick={() => setShowDeleteGroup(true)}
                            className="text-red-600 hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-900/20"
                        >
                            Delete Group
                        </Button>
                    )}
                </div>
            </div>

            <div className={`grid gap-6 mb-8 ${isDirect ? 'grid-cols-1' : 'grid-cols-1 lg:grid-cols-3'}`}>
                <div className={isDirect ? '' : 'lg:col-span-2'}>
                    <BillUpload groupId={groupId} />
                </div>

                {!isDirect && (
                    <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow dark:shadow-none dark:border dark:border-gray-700">
                        <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Group Members</h3>
                        {group?.members && group.members.length > 0 ? (
                            <div className="space-y-3">
                                {group.members.map((member) => (
                                    <div key={member.user_id} className="flex items-center justify-between">
                                        <div className="flex items-center">
                                            <div className="flex-shrink-0">
                                                <div className="h-8 w-8 rounded-full bg-primary-100 dark:bg-primary-900 flex items-center justify-center">
                                                    <span className="text-primary-600 dark:text-primary-400 font-medium text-sm">
                                                        {member.user_name?.charAt(0).toUpperCase() || 'U'}
                                                    </span>
                                                </div>
                                            </div>
                                            <div className="ml-3">
                                                <p className="text-sm font-medium text-gray-900 dark:text-white">{member.user_name}</p>
                                                <p className="text-xs text-gray-500 dark:text-gray-400">{member.user_email}</p>
                                            </div>
                                        </div>
                                        {isCreator && member.user_id !== user?.id && !isDirect && (
                                            <button
                                                onClick={() => setMemberToRemove(member)}
                                                className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300 text-sm"
                                                title="Remove member"
                                            >
                                                ✕
                                            </button>
                                        )}
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <p className="text-sm text-gray-600 dark:text-gray-400">No members yet</p>
                        )}
                    </div>
                )}
            </div>

            {
                (balances.length > 0 || debts.length > 0) && (
                    <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-none dark:border dark:border-gray-700 mb-8">
                        <div className="px-6 py-4 border-b dark:border-gray-700">
                            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Balances</h2>
                        </div>
                        <div className="p-6">
                            {/* Detailed Debts Section */}
                            {debts.length > 0 && (
                                <div className="mb-8">
                                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">Settlements Required</h3>
                                    <div className="space-y-3">
                                        {debts.map((debt, idx) => (
                                            <div key={idx} className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded border-l-4 border-red-400 dark:border-red-500">
                                                <span className="text-gray-700 dark:text-gray-200">
                                                    <span className="font-medium text-gray-900 dark:text-white">{debt.from_user}</span> owes <span className="font-medium text-gray-900 dark:text-white">{debt.to_user}</span>
                                                </span>
                                                <span className="font-bold text-gray-900 dark:text-white">
                                                    ₹{debt.amount}
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* User Stats Table */}
                            {balances.length > 0 && (
                                <>
                                    <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-3">Member Details</h3>
                                    <div className="overflow-x-auto">
                                        <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                                            <thead className="bg-gray-50 dark:bg-gray-700">
                                                <tr>
                                                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Member</th>
                                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Paid</th>
                                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Share</th>
                                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Settled</th>
                                                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Net Balance</th>
                                                </tr>
                                            </thead>
                                            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                                                {balances.map((balance) => (
                                                    <tr key={balance.user_id}>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                                                            {balance.user_name} {balance.user_id === user?.id && '(You)'}
                                                        </td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500 dark:text-gray-400">
                                                            ₹{balance.total_paid}
                                                        </td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right text-gray-500 dark:text-gray-400">
                                                            ₹{balance.total_share}
                                                        </td>
                                                        <td className={`px-6 py-4 whitespace-nowrap text-sm text-right ${parseFloat(balance.total_settled) > 0 ? 'text-green-600' : parseFloat(balance.total_settled) < 0 ? 'text-red-600' : 'text-gray-500'}`}>
                                                            {parseFloat(balance.total_settled) > 0 ? '+' : ''}{parseFloat(balance.total_settled) !== 0 ? `₹${parseFloat(balance.total_settled).toFixed(2)}` : '-'}
                                                        </td>
                                                        <td className={`px-6 py-4 whitespace-nowrap text-sm text-right font-semibold ${parseFloat(balance.net_balance) >= 0
                                                            ? 'text-green-600 dark:text-green-400'
                                                            : 'text-red-600 dark:text-red-400'
                                                            }`}>
                                                            {parseFloat(balance.net_balance) >= 0 ? '+' : ''}₹{parseFloat(balance.net_balance).toFixed(2)}
                                                            <span className="block text-xs font-normal text-gray-500">
                                                                {parseFloat(balance.net_balance) >= 0 ? 'gets back' : 'owes'}
                                                            </span>
                                                        </td>
                                                    </tr>
                                                ))}
                                            </tbody>
                                        </table>
                                    </div>
                                </>
                            )}
                        </div>
                    </div>
                )
            }

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-none dark:border dark:border-gray-700">
                <div className="px-6 py-4 border-b dark:border-gray-700">
                    <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Expenses</h2>
                </div>
                {expensesLoading ? (
                    <div className="p-12 text-center">
                        <Spinner />
                    </div>
                ) : expenses && expenses.length > 0 ? (
                    <div className="divide-y dark:divide-gray-700">
                        {expenses.map((expense) => (
                            <Link
                                key={expense.id}
                                to={`/expenses/${expense.id}`}
                                className="block p-6 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                            >
                                <div className="flex justify-between items-start">
                                    <div className="flex-1">
                                        <div className="flex items-center space-x-2">
                                            <h3 className="font-medium text-gray-900 dark:text-white">
                                                {expense.description || 'Expense'}
                                            </h3>
                                            <span className={`px-2 py-1 text-xs rounded-full ${expense.status === 'READY' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                                                expense.status === 'PROCESSING' ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200' :
                                                    expense.status === 'FAILED' ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200' :
                                                        'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                                                }`}>
                                                {expense.status}
                                            </span>
                                            {expense.source_type === 'BILL_IMAGE' && (
                                                <span className="text-xs text-primary-600 px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">Scanned</span>
                                            )}
                                        </div>
                                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                            Paid by {expense.creator_name || 'Unknown'} • {new Date(expense.created_at).toLocaleDateString()}
                                        </p>
                                    </div>
                                    <div className="text-right">
                                        <p className="font-semibold text-gray-900 dark:text-white">
                                            ₹{expense.total_amount || '0.00'}
                                        </p>
                                        {expense.items && (
                                            <p className="text-sm text-gray-600 dark:text-gray-400">{expense.items.length} items</p>
                                        )}
                                    </div>
                                </div>
                            </Link>
                        ))}
                    </div>
                ) : (
                    <div className="p-12 text-center">
                        <p className="text-gray-600 dark:text-gray-400">No expenses yet. Upload a bill to get started!</p>
                    </div>
                )}
            </div>

            {/* Add Member Modal */}
            <AddMemberModal
                isOpen={showAddMember}
                onClose={() => setShowAddMember(false)}
                groupId={groupId}
                existingMemberIds={group?.members?.map(m => m.user_id) || []}
                onSuccess={() => {
                    queryClient.invalidateQueries({ queryKey: ['groups', groupId] });
                }}
            />

            {/* Delete Group Confirmation */}
            <ConfirmDialog
                isOpen={showDeleteGroup}
                onClose={() => setShowDeleteGroup(false)}
                onConfirm={handleDeleteGroup}
                title="Delete Group?"
                message="This will permanently delete the group and all its expenses. This action cannot be undone."
                confirmText="Delete"
                confirmVariant="primary"
                isLoading={deleteGroupMutation.isPending}
            />

            {/* Leave Group Confirmation */}
            <ConfirmDialog
                isOpen={showLeaveGroup}
                onClose={() => setShowLeaveGroup(false)}
                onConfirm={handleLeaveGroup}
                title="Leave Group?"
                message="Are you sure you want to leave this group? You will lose access to the group's expenses."
                confirmText="Leave"
                confirmVariant="primary"
                isLoading={leaveGroupMutation.isPending}
            />

            <ConfirmDialog
                isOpen={!!memberToRemove}
                onClose={() => setMemberToRemove(null)}
                onConfirm={handleRemoveMember}
                title="Remove Member?"
                message={`Are you sure you want to remove ${memberToRemove?.user_name} from this group?`}
                confirmText="Remove"
                confirmVariant="primary"
                isLoading={removeMemberMutation.isPending}
            />

            {/* Settlement Modal */}
            <SettlementModal
                isOpen={showSettlementModal}
                onClose={() => setShowSettlementModal(false)}
                groupId={groupId}
                members={group?.members || []}
                debts={debts}
            />
        </Layout >
    );
};
