import { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { groupsAPI } from '../../api/groups';
import { Dialog } from '../common/Dialog';
import { Button } from '../common/Button';
import { useAuth } from '../../context/AuthContext';

export const SettlementModal = ({ isOpen, onClose, groupId, members = [], debts = [] }) => {
    const { user } = useAuth();
    const queryClient = useQueryClient();

    // Form state
    const [paidTo, setPaidTo] = useState('');
    const [amount, setAmount] = useState('');
    const [paymentMethod, setPaymentMethod] = useState('CASH');
    const [note, setNote] = useState('');
    const [error, setError] = useState('');

    // Auto-select payee if there's only one logical person to pay (simplified debt suggestion)
    useEffect(() => {
        if (isOpen && debts.length > 0 && user) {
            // Find debts where current user is the "from_user"
            // Note: debts provided by backend have "from_user" as NAME, not ID.
            // We need to match names to member IDs.
            // But wait, the API returns user_name in debts list.
            // Let's rely on members list for selection, but use debts to suggest.

            const myDebt = debts.find(d => d.from_user === user.name);
            if (myDebt) {
                // Find member with this name to get ID
                const targetMember = members.find(m => m.user_name === myDebt.to_user);
                if (targetMember) {
                    setPaidTo(targetMember.user_id);
                    setAmount(myDebt.amount.toString());
                }
            }
        } else if (isOpen) {
            // Reset form
            setPaidTo('');
            setAmount('');
            setPaymentMethod('CASH');
            setNote('');
            setError('');
        }
    }, [isOpen, debts, user, members]);

    const mutation = useMutation({
        mutationFn: (data) => groupsAPI.recordSettlement(data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['groups', groupId] });
            queryClient.invalidateQueries({ queryKey: ['balances', groupId] });
            onClose();
        },
        onError: (err) => {
            setError(err.response?.data?.detail || 'Failed to record settlement');
        }
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        setError('');

        if (!paidTo) {
            setError('Please select who you paid.');
            return;
        }

        if (!amount || parseFloat(amount) <= 0) {
            setError('Please enter a valid amount.');
            return;
        }

        mutation.mutate({
            group_id: groupId,
            paid_to: paidTo,
            amount: parseFloat(amount),
            payment_method: paymentMethod,
            note: note
        });
    };

    const paymentMethods = [
        { value: 'CASH', label: 'Cash' },
        { value: 'UPI', label: 'UPI' },
        { value: 'BANK', label: 'Bank Transfer' },
        { value: 'OTHER', label: 'Other' }
    ];

    // Filter out current user from payee list
    const potentialPayees = members.filter(m => m.user_id !== user?.id);

    return (
        <Dialog isOpen={isOpen} onClose={onClose} title="Settle Up">
            <form onSubmit={handleSubmit} className="space-y-4">
                {error && (
                    <div className="bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400 p-3 rounded text-sm">
                        {error}
                    </div>
                )}

                <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Paid To
                    </label>
                    <select
                        value={paidTo}
                        onChange={(e) => setPaidTo(e.target.value)}
                        className="w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-primary-500 focus:ring-primary-500"
                        required
                    >
                        <option value="">Select a member</option>
                        {potentialPayees.map(member => (
                            <option key={member.user_id} value={member.user_id}>
                                {member.user_name} ({member.user_email})
                            </option>
                        ))}
                    </select>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Amount
                    </label>
                    <div className="relative rounded-md shadow-sm">
                        <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
                            <span className="text-gray-500 sm:text-sm">₹</span>
                        </div>
                        <input
                            type="number"
                            step="0.01"
                            min="0.01"
                            value={amount}
                            onChange={(e) => setAmount(e.target.value)}
                            className="block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white pl-7 py-2 focus:border-primary-500 focus:ring-primary-500"
                            placeholder="0.00"
                            required
                        />
                    </div>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Payment Method
                    </label>
                    <div className="flex flex-wrap gap-2">
                        {paymentMethods.map(method => (
                            <button
                                key={method.value}
                                type="button"
                                onClick={() => setPaymentMethod(method.value)}
                                className={`px-3 py-1.5 text-sm font-medium rounded-full transition-colors ${paymentMethod === method.value
                                        ? 'bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200 ring-2 ring-primary-500'
                                        : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                                    }`}
                            >
                                {method.label}
                            </button>
                        ))}
                    </div>
                </div>

                <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                        Note (Optional)
                    </label>
                    <textarea
                        value={note}
                        onChange={(e) => setNote(e.target.value)}
                        rows={2}
                        className="w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-primary-500 focus:ring-primary-500"
                        placeholder="What was this for?"
                    />
                </div>

                <div className="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
                    <Button
                        type="submit"
                        isLoading={mutation.isPending}
                        className="w-full sm:col-start-2"
                    >
                        Record Payment
                    </Button>
                    <Button
                        type="button"
                        variant="secondary"
                        onClick={onClose}
                        className="mt-3 w-full sm:mt-0 sm:col-start-1"
                    >
                        Cancel
                    </Button>
                </div>
            </form>
        </Dialog>
    );
};
