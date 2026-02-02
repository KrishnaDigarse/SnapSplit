import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { groupsAPI } from '../api/groups';
import { Layout } from '../components/layout/Layout';
import { Button } from '../components/common/Button';
import { Input } from '../components/common/Input';
import { Spinner } from '../components/common/Spinner';
import { ErrorMessage } from '../components/common/ErrorMessage';

export const Groups = () => {
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [groupName, setGroupName] = useState('');
    const [error, setError] = useState('');
    const queryClient = useQueryClient();

    const { data: groups, isLoading } = useQuery({
        queryKey: ['groups'],
        queryFn: groupsAPI.getGroups
    });

    const createGroupMutation = useMutation({ // Renamed createMutation to createGroupMutation
        mutationFn: (name) => groupsAPI.createGroup({ name }), // Kept original mutationFn structure for simplicity based on existing handleCreate
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['groups'] });
            setGroupName(''); // Retained setGroupName for existing input
            setShowCreateForm(false); // Retained setShowCreateForm for existing form visibility
            // setError(''); // Removed setError
            toast.success('Group created successfully!'); // Added success toast
        },
        onError: (err) => {
            // setError(err.response?.data?.detail || 'Failed to create group'); // Removed setError
            toast.error(err.response?.data?.detail || 'Failed to create group'); // Added error toast
        }
    });

    const handleCreate = (e) => {
        e.preventDefault();
        if (!groupName.trim()) {
            setError('Group name is required');
            return;
        }
        createGroupMutation.mutate({ name: groupName });
    };

    return (
        <Layout>
            <div className="mb-8 flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Groups</h1>
                    <p className="mt-2 text-gray-600 dark:text-gray-400">Manage your expense groups</p>
                </div>
                <Button onClick={() => setShowCreateForm(!showCreateForm)}>
                    {showCreateForm ? 'Cancel' : '+ Create Group'}
                </Button>
            </div>

            {showCreateForm && (
                <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow dark:shadow-none dark:border dark:border-gray-700 mb-6">
                    <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Create New Group</h3>
                    {error && <ErrorMessage message={error} />}
                    <form onSubmit={handleCreate}>
                        <Input
                            label="Group Name"
                            type="text"
                            value={groupName}
                            onChange={(e) => setGroupName(e.target.value)}
                            placeholder="e.g., Roommates, Trip to Goa"
                            required
                        />
                        <Button type="submit" loading={createGroupMutation.isPending}>
                            Create Group
                        </Button>
                    </form>
                </div>
            )}

            {isLoading ? (
                <div className="text-center py-12">
                    <Spinner size="lg" />
                </div>
            ) : groups && groups.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {groups.map((group) => (
                        <Link
                            key={group.id}
                            to={`/groups/${group.id}`}
                            className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow dark:shadow-none dark:border dark:border-gray-700 hover:shadow-lg transition-shadow"
                        >
                            <div className="flex items-start justify-between">
                                <div className="flex-1">
                                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{group.name}</h3>
                                    <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                                        {group.member_count || 0} members
                                    </p>
                                </div>
                                <svg className="h-5 w-5 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                                </svg>
                            </div>
                            <div className="mt-4 pt-4 border-t dark:border-gray-700">
                                <p className="text-sm text-gray-500 dark:text-gray-400">
                                    Created {new Date(group.created_at).toLocaleDateString()}
                                </p>
                            </div>
                        </Link>
                    ))}
                </div>
            ) : (
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-none dark:border dark:border-gray-700 p-12 text-center">
                    <svg className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                    <h3 className="mt-4 text-lg font-medium text-gray-900 dark:text-white">No groups yet</h3>
                    <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                        Create a group to start splitting expenses with friends.
                    </p>
                    <Button className="mt-4" onClick={() => setShowCreateForm(true)}>
                        Create Your First Group
                    </Button>
                </div>
            )}
        </Layout>
    );
};
