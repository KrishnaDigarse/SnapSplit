import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { friendsAPI } from '../../api/friends';
import { Button } from '../common/Button';
import { Spinner } from '../common/Spinner';

export const AddMemberModal = ({ isOpen, onClose, groupId, existingMemberIds, onSuccess }) => {
    const [selectedFriendId, setSelectedFriendId] = useState('');
    const [error, setError] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const { data: friends, isLoading } = useQuery({
        queryKey: ['friends'],
        queryFn: friendsAPI.getFriends,
        enabled: isOpen
    });

    // Filter out friends who are already members
    const availableFriends = friends?.filter(
        friend => !existingMemberIds.includes(friend.friend_id)
    ) || [];

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!selectedFriendId) {
            setError('Please select a friend');
            return;
        }

        setIsSubmitting(true);
        setError('');

        try {
            const { groupsAPI } = await import('../../api/groups');
            await groupsAPI.addMember(groupId, selectedFriendId);
            onSuccess();
            onClose();
            setSelectedFriendId('');
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to add member');
        } finally {
            setIsSubmitting(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full mx-4">
                <div className="p-6">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                        Add Member to Group
                    </h3>

                    {isLoading ? (
                        <div className="py-8 text-center">
                            <Spinner />
                        </div>
                    ) : availableFriends.length === 0 ? (
                        <div className="py-8 text-center">
                            <p className="text-gray-600 dark:text-gray-400">
                                No friends available to add. All your friends are already members!
                            </p>
                        </div>
                    ) : (
                        <form onSubmit={handleSubmit}>
                            {error && (
                                <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded text-red-600 dark:text-red-400 text-sm">
                                    {error}
                                </div>
                            )}

                            <div className="mb-6">
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                    Select Friend
                                </label>
                                <select
                                    value={selectedFriendId}
                                    onChange={(e) => setSelectedFriendId(e.target.value)}
                                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                                    required
                                >
                                    <option value="">Choose a friend...</option>
                                    {availableFriends.map((friend) => (
                                        <option key={friend.friend_id} value={friend.friend_id}>
                                            {friend.friend_name} ({friend.friend_email})
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div className="flex justify-end space-x-3">
                                <Button
                                    type="button"
                                    variant="secondary"
                                    onClick={onClose}
                                    disabled={isSubmitting}
                                >
                                    Cancel
                                </Button>
                                <Button
                                    type="submit"
                                    loading={isSubmitting}
                                >
                                    Add Member
                                </Button>
                            </div>
                        </form>
                    )}
                </div>
            </div>
        </div>
    );
};
