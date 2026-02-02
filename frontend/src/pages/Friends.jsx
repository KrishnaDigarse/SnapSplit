import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { friendsAPI } from '../api/friends';
import { groupsAPI } from '../api/groups';
import { Layout } from '../components/layout/Layout';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { Spinner } from '../components/common/Spinner';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { ConfirmDialog } from '../components/common/ConfirmDialog';
import { useNavigate } from 'react-router-dom';

export const Friends = () => {
    const [showAddForm, setShowAddForm] = useState(false);
    const [friendEmail, setFriendEmail] = useState('');
    const [error, setError] = useState('');
    const [friendToRemove, setFriendToRemove] = useState(null);
    const queryClient = useQueryClient();
    const navigate = useNavigate();

    const { data: friends, isLoading: friendsLoading } = useQuery({
        queryKey: ['friends'],
        queryFn: friendsAPI.getFriends
    });

    const { data: pendingRequests, isLoading: requestsLoading } = useQuery({
        queryKey: ['friend-requests'],
        queryFn: friendsAPI.getPendingRequests
    });

    // Get all groups to find DIRECT groups
    const { data: allGroups } = useQuery({
        queryKey: ['all-groups'],
        queryFn: async () => {
            // We need to get ALL groups including DIRECT ones
            // The current API filters out DIRECT groups, so we'll navigate using friend_id
            return [];
        }
    });

    const sendRequestMutation = useMutation({
        mutationFn: (email) => friendsAPI.sendFriendRequest(email),
        onSuccess: () => {
            setFriendEmail('');
            setShowAddForm(false);
            setError('');
            toast.success('Friend request sent!');
        },
        onError: (err) => {
            setError(err.response?.data?.detail || 'Failed to send friend request');
            toast.error(err.response?.data?.detail || 'Failed to send request');
        }
    });

    const acceptRequestMutation = useMutation({
        mutationFn: (requestId) => friendsAPI.acceptFriendRequest(requestId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['friends'] });
            queryClient.invalidateQueries({ queryKey: ['friend-requests'] });
            toast.success('Friend request accepted!');
        },
        onError: () => toast.error('Failed to accept request')
    });

    const rejectRequestMutation = useMutation({
        mutationFn: (requestId) => friendsAPI.rejectFriendRequest(requestId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['friend-requests'] });
            toast.success('Friend request rejected');
        },
        onError: () => toast.error('Failed to reject request')
    });

    const removeFriendMutation = useMutation({
        mutationFn: (friendId) => friendsAPI.removeFriend(friendId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['friends'] });
            queryClient.invalidateQueries({ queryKey: ['groups'] });
            setFriendToRemove(null);
            toast.success('Friend removed');
        },
        onError: () => toast.error('Failed to remove friend')
    });

    const handleSendRequest = (e) => {
        e.preventDefault();
        if (!friendEmail.trim()) {
            setError('Email is required');
            return;
        }
        sendRequestMutation.mutate(friendEmail);
    };

    const handleRemoveFriend = () => {
        if (friendToRemove) {
            removeFriendMutation.mutate(friendToRemove.friend_id);
        }
    };

    const handleViewExpenses = async (friend) => {
        try {
            const directGroup = await friendsAPI.getDirectGroup(friend.friend_id);
            navigate(`/groups/${directGroup.group_id}`);
        } catch (error) {
            console.error('Failed to get direct group:', error);
            // Fallback to groups page if DIRECT group not found
            navigate('/groups');
        }
    };

    return (
        <Layout>
            <div className="mb-8 flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Friends</h1>
                    <p className="mt-2 text-gray-600 dark:text-gray-400">Manage your connections</p>
                </div>
                <Button onClick={() => setShowAddForm(!showAddForm)}>
                    {showAddForm ? 'Cancel' : '+ Add Friend'}
                </Button>
            </div>

            {showAddForm && (
                <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow dark:shadow-none dark:border dark:border-gray-700 mb-6">
                    <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Send Friend Request</h3>
                    {error && <ErrorMessage message={error} />}
                    <form onSubmit={handleSendRequest}>
                        <Input
                            label="Friend's Email"
                            type="email"
                            value={friendEmail}
                            onChange={(e) => setFriendEmail(e.target.value)}
                            placeholder="friend@example.com"
                            required
                        />
                        <Button type="submit" loading={sendRequestMutation.isPending}>
                            Send Request
                        </Button>
                    </form>
                </div>
            )}

            {pendingRequests && pendingRequests.length > 0 && (
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-none dark:border dark:border-gray-700 mb-6">
                    <div className="px-6 py-4 border-b dark:border-gray-700">
                        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Pending Requests</h2>
                    </div>
                    <div className="divide-y dark:divide-gray-700">
                        {pendingRequests.map((request) => (
                            <div key={request.id} className="p-6 flex justify-between items-center">
                                <div>
                                    <p className="font-medium text-gray-900 dark:text-white">{request.sender_name}</p>
                                    <p className="text-sm text-gray-600 dark:text-gray-400">{request.sender_email}</p>
                                </div>
                                <div className="flex space-x-2">
                                    <Button
                                        size="sm"
                                        onClick={() => acceptRequestMutation.mutate(request.id)}
                                        loading={acceptRequestMutation.isPending}
                                    >
                                        Accept
                                    </Button>
                                    <Button
                                        size="sm"
                                        variant="secondary"
                                        onClick={() => rejectRequestMutation.mutate(request.id)}
                                        loading={rejectRequestMutation.isPending}
                                    >
                                        Reject
                                    </Button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-none dark:border dark:border-gray-700">
                <div className="px-6 py-4 border-b dark:border-gray-700">
                    <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Your Friends</h2>
                </div>
                {friendsLoading || requestsLoading ? (
                    <div className="p-12 text-center">
                        <Spinner size="lg" />
                    </div>
                ) : friends && friends.length > 0 ? (
                    <div className="divide-y dark:divide-gray-700">
                        {friends.map((friend) => (
                            <div key={friend.friend_id} className="p-6 flex justify-between items-center">
                                <div className="flex-1">
                                    <p className="font-medium text-gray-900 dark:text-white">{friend.friend_name}</p>
                                    <p className="text-sm text-gray-600 dark:text-gray-400">{friend.friend_email}</p>
                                </div>
                                <div className="flex items-center space-x-3">
                                    <Button
                                        size="sm"
                                        variant="secondary"
                                        onClick={() => handleViewExpenses(friend)}
                                    >
                                        View Expenses
                                    </Button>
                                    <button
                                        onClick={() => setFriendToRemove(friend)}
                                        className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300 text-sm font-medium"
                                        title="Remove friend"
                                    >
                                        Unfriend
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="p-12 text-center">
                        <svg className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                        </svg>
                        <h3 className="mt-4 text-lg font-medium text-gray-900 dark:text-white">No friends yet</h3>
                        <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                            Add friends to start splitting expenses together.
                        </p>
                    </div>
                )}
            </div>

            {/* Remove Friend Confirmation */}
            <ConfirmDialog
                isOpen={!!friendToRemove}
                onClose={() => setFriendToRemove(null)}
                onConfirm={handleRemoveFriend}
                title="Remove Friend?"
                message={`Are you sure you want to unfriend ${friendToRemove?.friend_name}? This will also delete your shared expense history.`}
                confirmText="Unfriend"
                confirmVariant="primary"
                isLoading={removeFriendMutation.isPending}
            />
        </Layout>
    );
};
