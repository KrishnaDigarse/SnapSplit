import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { friendsAPI } from '../api/friends';
import { Layout } from '../components/layout/Layout';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { Spinner } from '../components/common/Spinner';
import { ErrorMessage } from '../components/common/ErrorMessage';

export const Friends = () => {
    const [showAddForm, setShowAddForm] = useState(false);
    const [friendEmail, setFriendEmail] = useState('');
    const [error, setError] = useState('');
    const queryClient = useQueryClient();

    const { data: friends, isLoading: friendsLoading } = useQuery({
        queryKey: ['friends'],
        queryFn: friendsAPI.getFriends
    });

    const { data: pendingRequests, isLoading: requestsLoading } = useQuery({
        queryKey: ['friend-requests'],
        queryFn: friendsAPI.getPendingRequests
    });

    const sendRequestMutation = useMutation({
        mutationFn: (email) => friendsAPI.sendFriendRequest(email),
        onSuccess: () => {
            setFriendEmail('');
            setShowAddForm(false);
            setError('');
        },
        onError: (err) => {
            setError(err.response?.data?.detail || 'Failed to send friend request');
        }
    });

    const acceptMutation = useMutation({
        mutationFn: (requestId) => friendsAPI.acceptFriendRequest(requestId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['friends'] });
            queryClient.invalidateQueries({ queryKey: ['friend-requests'] });
        }
    });

    const rejectMutation = useMutation({
        mutationFn: (requestId) => friendsAPI.rejectFriendRequest(requestId),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['friend-requests'] });
        }
    });

    const handleSendRequest = (e) => {
        e.preventDefault();
        if (!friendEmail.trim()) {
            setError('Email is required');
            return;
        }
        sendRequestMutation.mutate(friendEmail);
    };

    return (
        <Layout>
            <div className="mb-8 flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">Friends</h1>
                    <p className="mt-2 text-gray-600">Manage your connections</p>
                </div>
                <Button onClick={() => setShowAddForm(!showAddForm)}>
                    {showAddForm ? 'Cancel' : '+ Add Friend'}
                </Button>
            </div>

            {showAddForm && (
                <div className="bg-white p-6 rounded-lg shadow mb-6">
                    <h3 className="text-lg font-semibold mb-4">Send Friend Request</h3>
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
                <div className="bg-white rounded-lg shadow mb-6">
                    <div className="px-6 py-4 border-b">
                        <h2 className="text-xl font-semibold text-gray-900">Pending Requests</h2>
                    </div>
                    <div className="divide-y">
                        {pendingRequests.map((request) => (
                            <div key={request.id} className="p-6 flex justify-between items-center">
                                <div>
                                    <p className="font-medium text-gray-900">{request.sender_name}</p>
                                    <p className="text-sm text-gray-600">{request.sender_email}</p>
                                </div>
                                <div className="flex space-x-2">
                                    <Button
                                        size="sm"
                                        onClick={() => acceptMutation.mutate(request.id)}
                                        loading={acceptMutation.isPending}
                                    >
                                        Accept
                                    </Button>
                                    <Button
                                        size="sm"
                                        variant="secondary"
                                        onClick={() => rejectMutation.mutate(request.id)}
                                        loading={rejectMutation.isPending}
                                    >
                                        Reject
                                    </Button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            <div className="bg-white rounded-lg shadow">
                <div className="px-6 py-4 border-b">
                    <h2 className="text-xl font-semibold text-gray-900">Your Friends</h2>
                </div>
                {friendsLoading || requestsLoading ? (
                    <div className="p-12 text-center">
                        <Spinner size="lg" />
                    </div>
                ) : friends && friends.length > 0 ? (
                    <div className="divide-y">
                        {friends.map((friend) => (
                            <div key={friend.id} className="p-6 flex justify-between items-center">
                                <div>
                                    <p className="font-medium text-gray-900">{friend.name}</p>
                                    <p className="text-sm text-gray-600">{friend.email}</p>
                                </div>
                                <span className="text-sm text-green-600">✓ Friends</span>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="p-12 text-center">
                        <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                        </svg>
                        <h3 className="mt-4 text-lg font-medium text-gray-900">No friends yet</h3>
                        <p className="mt-2 text-sm text-gray-600">
                            Add friends to start splitting expenses together.
                        </p>
                    </div>
                )}
            </div>
        </Layout>
    );
};
