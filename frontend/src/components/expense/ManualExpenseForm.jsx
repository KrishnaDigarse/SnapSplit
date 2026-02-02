import { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { expensesAPI } from '../../api/expenses';
import { Button } from '../common/Button';
import { Input } from '../common/Input';
import { Spinner } from '../common/Spinner';

export const ManualExpenseForm = ({ groupId, members, onSuccess, onCancel }) => {
    const queryClient = useQueryClient();

    const [description, setDescription] = useState('');
    const [totalAmount, setTotalAmount] = useState(''); // String for input, parse to float
    const [category, setCategory] = useState('Other');
    const [splitType, setSplitType] = useState('EQUAL'); // 'EQUAL' or 'CUSTOM'
    const [selectedMemberIds, setSelectedMemberIds] = useState(new Set(members.map(m => m.user_id)));
    const [customAmounts, setCustomAmounts] = useState({}); // userId -> amount
    const [errors, setErrors] = useState({});

    // Initialize custom amounts when members change or split type changes
    useEffect(() => {
        if (splitType === 'CUSTOM') {
            const initialAmounts = {};
            members.forEach(m => {
                if (selectedMemberIds.has(m.user_id)) {
                    initialAmounts[m.user_id] = customAmounts[m.user_id] || '';
                }
            });
            setCustomAmounts(initialAmounts);
        }
    }, [selectedMemberIds, splitType]);

    const createMutation = useMutation({
        mutationFn: (data) => expensesAPI.createManualExpense(data),
        onSuccess: () => {
            toast.success('Expense created successfully!');
            queryClient.invalidateQueries({ queryKey: ['groups', groupId] }); // Refresh balances/expenses
            queryClient.invalidateQueries({ queryKey: ['expenses'] });
            onSuccess();
        },
        onError: (err) => {
            toast.error(err.response?.data?.detail || 'Failed to create expense');
        }
    });

    const handleMemberToggle = (userId) => {
        const newSelected = new Set(selectedMemberIds);
        if (newSelected.has(userId)) {
            newSelected.delete(userId);
        } else {
            newSelected.add(userId);
        }
        setSelectedMemberIds(newSelected);

        // Remove amount if unselected
        if (!newSelected.has(userId)) {
            const newAmounts = { ...customAmounts };
            delete newAmounts[userId];
            setCustomAmounts(newAmounts);
        }
    };

    const validate = () => {
        const newErrors = {};
        const amount = parseFloat(totalAmount);

        if (!description.trim()) newErrors.description = 'Description is required';
        if (!totalAmount || isNaN(amount) || amount <= 0) newErrors.totalAmount = 'Valid amount is required';
        if (selectedMemberIds.size < 2) newErrors.members = 'Select at least 2 participants';

        if (splitType === 'CUSTOM' && amount > 0) {
            let sum = 0;
            selectedMemberIds.forEach(id => {
                const val = parseFloat(customAmounts[id]) || 0;
                sum += val;
            });

            if (Math.abs(sum - amount) > 0.05) { // 0.05 tolerance for floating point
                newErrors.split = `Total split (${sum.toFixed(2)}) must equal expense amount (${amount.toFixed(2)})`;
            }
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!validate()) return;

        const amount = parseFloat(totalAmount);

        // Calculate splits
        const splits = [];
        if (splitType === 'EQUAL') {
            // Logic to handle cents correctly
            const count = selectedMemberIds.size;
            const baseAmount = Math.floor((amount / count) * 100) / 100;
            const remainder = Math.round((amount - (baseAmount * count)) * 100);

            let i = 0;
            selectedMemberIds.forEach(userId => {
                let splitAmount = baseAmount;
                if (i < remainder) {
                    splitAmount += 0.01;
                }
                splits.push({
                    user_id: userId,
                    amount: splitAmount
                });
                i++;
            });
        } else {
            selectedMemberIds.forEach(userId => {
                splits.push({
                    user_id: userId,
                    amount: parseFloat(customAmounts[userId]) || 0
                });
            });
        }

        const payload = {
            group_id: groupId,
            subtotal: amount,
            tax: 0,
            total_amount: amount,
            items: [
                {
                    item_name: description,
                    quantity: 1,
                    price: amount
                }
            ],
            splits: splits.map(s => ({
                user_id: s.user_id,
                amount: s.amount,
                split_type: splitType
            }))
        };

        createMutation.mutate(payload);
    };

    return (
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow dark:shadow-none dark:border dark:border-gray-700">
            <h3 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">Add Expense</h3>

            <form onSubmit={handleSubmit} className="space-y-4">
                <Input
                    label="Description"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="e.g. Dinner at Taj"
                    error={errors.description}
                    required
                />

                <div className="grid grid-cols-2 gap-4">
                    <Input
                        label="Amount (₹)"
                        type="number"
                        value={totalAmount}
                        onChange={(e) => setTotalAmount(e.target.value)}
                        placeholder="0.00"
                        error={errors.totalAmount}
                        required
                    />
                    <div className="mb-4">
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Category</label>
                        <select
                            value={category}
                            onChange={(e) => setCategory(e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        >
                            <option value="Food">Food 🍔</option>
                            <option value="Travel">Travel ✈️</option>
                            <option value="Entertainment">Entertainment 🎬</option>
                            <option value="Home">Home 🏠</option>
                            <option value="Other">Other 📝</option>
                        </select>
                    </div>
                </div>

                {/* Split Type Toggle */}
                <div className="flex space-x-2 mb-4">
                    <button
                        type="button"
                        onClick={() => setSplitType('EQUAL')}
                        className={`flex-1 py-2 text-sm font-medium rounded-lg transition-colors ${splitType === 'EQUAL'
                            ? 'bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200 border-2 border-primary-500'
                            : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                            }`}
                    >
                        Split Equally (=)
                    </button>
                    <button
                        type="button"
                        onClick={() => setSplitType('CUSTOM')}
                        className={`flex-1 py-2 text-sm font-medium rounded-lg transition-colors ${splitType === 'CUSTOM'
                            ? 'bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200 border-2 border-primary-500'
                            : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                            }`}
                    >
                        Custom Split
                    </button>
                </div>

                {/* Participants List */}
                <div className="space-y-2 max-h-60 overflow-y-auto p-2 border dark:border-gray-700 rounded-lg">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Split with ({selectedMemberIds.size} selected)
                    </label>
                    {errors.members && <p className="text-sm text-red-600 dark:text-red-400 mb-2">{errors.members}</p>}

                    {members.map(member => (
                        <div key={member.user_id} className="flex items-center justify-between py-2 border-b last:border-0 dark:border-gray-700">
                            <label className="flex items-center flex-1 cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={selectedMemberIds.has(member.user_id)}
                                    onChange={() => handleMemberToggle(member.user_id)}
                                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                                />
                                <span className={`ml-3 text-sm ${selectedMemberIds.has(member.user_id) ? 'text-gray-900 dark:text-white font-medium' : 'text-gray-500 dark:text-gray-400'}`}>
                                    {member.user_name}
                                </span>
                            </label>

                            {splitType === 'CUSTOM' && selectedMemberIds.has(member.user_id) && (
                                <div className="flex items-center w-24">
                                    <span className="text-gray-500 dark:text-gray-400 mr-1">₹</span>
                                    <input
                                        type="number"
                                        value={customAmounts[member.user_id] || ''}
                                        onChange={(e) => setCustomAmounts({ ...customAmounts, [member.user_id]: e.target.value })}
                                        className="w-full text-sm border-b border-gray-300 dark:border-gray-600 focus:border-primary-500 focus:outline-none bg-transparent text-gray-900 dark:text-white text-right"
                                        placeholder="0"
                                    />
                                </div>
                            )}

                            {splitType === 'EQUAL' && selectedMemberIds.has(member.user_id) && totalAmount && (
                                <span className="text-sm text-gray-500 dark:text-gray-400">
                                    ~ ₹{(parseFloat(totalAmount) / selectedMemberIds.size).toFixed(2)}
                                </span>
                            )}
                        </div>
                    ))}
                </div>

                {errors.split && (
                    <div className="p-3 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300 text-sm rounded-lg">
                        {errors.split}
                    </div>
                )}

                <div className="flex justify-end space-x-3 pt-4">
                    <Button variant="secondary" onClick={onCancel} disabled={createMutation.isPending}>
                        Cancel
                    </Button>
                    <Button type="submit" loading={createMutation.isPending}>
                        Create Expense
                    </Button>
                </div>
            </form>
        </div>
    );
};
