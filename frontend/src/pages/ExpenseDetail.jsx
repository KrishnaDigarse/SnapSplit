import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { expensesAPI } from '../api/expenses';
import { Layout } from '../components/layout/Layout';
import { Spinner } from '../components/common/Spinner';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { Button } from '../components/common/Button';

export const ExpenseDetail = () => {
    const { expenseId } = useParams();
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    const [isEditing, setIsEditing] = useState(false);
    const [editForm, setEditForm] = useState(null);

    const { data: expense, isLoading } = useQuery({
        queryKey: ['expenses', expenseId],
        queryFn: () => expensesAPI.getExpenseDetail(expenseId)
    });

    // Initialize form when entering edit mode
    useEffect(() => {
        if (isEditing && expense) {
            setEditForm({
                description: expense.description || '',
                items: expense.items.map(item => ({
                    ...item,
                    price: parseFloat(item.price),
                    quantity: parseInt(item.quantity)
                })),
                tax: parseFloat(expense.tax || 0),
                subtotal: parseFloat(expense.subtotal || 0),
                total_amount: parseFloat(expense.total_amount || 0)
            });
        }
    }, [isEditing, expense]);

    // Auto-calculate totals when items or tax change
    useEffect(() => {
        if (editForm) {
            const calculatedSubtotal = editForm.items.reduce((sum, item) => {
                return sum + (item.price * item.quantity);
            }, 0);

            const calculatedTotal = calculatedSubtotal + (parseFloat(editForm.tax) || 0);

            if (calculatedSubtotal !== editForm.subtotal || calculatedTotal !== editForm.total_amount) {
                setEditForm(prev => ({
                    ...prev,
                    subtotal: calculatedSubtotal,
                    total_amount: calculatedTotal
                }));
            }
        }
    }, [editForm?.items, editForm?.tax]);

    const updateMutation = useMutation({
        mutationFn: (data) => expensesAPI.updateExpense(expenseId, data),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['expenses'] });
            setIsEditing(false);
        },
        onError: (error) => {
            alert('Failed to update expense: ' + (error.response?.data?.detail || error.message));
        }
    });

    const handleSave = () => {
        // Validate
        if (editForm.items.length === 0) {
            alert('Please add at least one item');
            return;
        }

        const payload = {
            description: editForm.description,
            items: editForm.items.map(item => ({
                item_name: item.item_name,
                quantity: parseInt(item.quantity),
                price: parseFloat(item.price)
            })),
            tax: parseFloat(editForm.tax),
            subtotal: parseFloat(editForm.subtotal),
            total_amount: parseFloat(editForm.total_amount)
        };

        updateMutation.mutate(payload);
    };

    const handleAddItem = () => {
        setEditForm(prev => ({
            ...prev,
            items: [...prev.items, { item_name: '', quantity: 1, price: 0 }]
        }));
    };

    const handleRemoveItem = (index) => {
        setEditForm(prev => ({
            ...prev,
            items: prev.items.filter((_, i) => i !== index)
        }));
    };

    const handleItemChange = (index, field, value) => {
        setEditForm(prev => {
            const newItems = [...prev.items];
            newItems[index] = { ...newItems[index], [field]: value };
            return { ...prev, items: newItems };
        });
    };

    if (isLoading) {
        return (
            <Layout>
                <div className="text-center py-12">
                    <Spinner size="lg" />
                </div>
            </Layout>
        );
    }

    if (!expense) {
        return (
            <Layout>
                <ErrorMessage message="Expense not found" />
            </Layout>
        );
    }

    const statusColors = {
        READY: 'bg-green-100 text-green-800',
        PROCESSING: 'bg-yellow-100 text-yellow-800',
        FAILED: 'bg-red-100 text-red-800',
        PENDING: 'bg-gray-100 text-gray-800'
    };

    return (
        <Layout>
            <div className="mb-6 flex justify-between items-center">
                <Link to={`/groups/${expense.group_id}`} className="text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 text-sm">
                    ← Back to Group
                </Link>
                {!isEditing && (
                    <div className="flex space-x-3">
                        <Button variant="secondary" onClick={() => setIsEditing(true)}>
                            ✏️ Edit / Fix (Missing Items)
                        </Button>
                        <Button onClick={() => navigate(`/groups/${expense.group_id}`)}>
                            ✅ Done
                        </Button>
                    </div>
                )}
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-none dark:border dark:border-gray-700 mb-6">
                <div className="px-6 py-4 border-b dark:border-gray-700">
                    <div className="flex justify-between items-start">
                        <div className="flex-1">
                            {isEditing ? (
                                <input
                                    type="text"
                                    value={editForm?.description}
                                    onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                                    className="text-2xl font-bold text-gray-900 dark:text-white border-b border-gray-300 dark:border-gray-600 bg-transparent focus:border-primary-500 focus:outline-none w-full"
                                    placeholder="Expense Description"
                                />
                            ) : (
                                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                                    {expense.description || 'Expense Details'}
                                </h1>
                            )}
                            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                Created on {new Date(expense.created_at).toLocaleDateString()}
                            </p>
                        </div>
                        {!isEditing && (
                            <div className="flex items-center space-x-2 ml-4">
                                <span className={`px-3 py-1 text-sm rounded-full ${statusColors[expense.status]}`}>
                                    {expense.status}
                                </span>
                                {expense.source_type === 'BILL_IMAGE' && (
                                    <span className="px-3 py-1 text-sm bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-200 rounded-full">
                                        🤖 AI Scanned
                                    </span>
                                )}
                            </div>
                        )}
                    </div>
                </div>

                {expense.status === 'FAILED' && !isEditing && (
                    <div className="p-6 border-b dark:border-gray-700">
                        <ErrorMessage
                            message="AI processing failed for this bill. The image may be unclear or the format is not supported."
                            action={
                                <Link to={`/groups/${expense.group_id}`}>
                                    <Button size="sm">Try Another Image</Button>
                                </Link>
                            }
                        />
                    </div>
                )}

                <div className="p-6">
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                        <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                            <p className="text-sm text-gray-600 dark:text-gray-400">Subtotal</p>
                            <p className="text-2xl font-bold text-gray-900 dark:text-white">
                                ₹{isEditing ? (editForm?.subtotal?.toFixed(2) || '0.00') : (expense.subtotal || '0.00')}
                            </p>
                        </div>
                        <div className="bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                            <p className="text-sm text-gray-600 dark:text-gray-400">Tax</p>
                            {isEditing ? (
                                <div className="flex items-center">
                                    <span className="text-2xl font-bold text-gray-900 dark:text-white mr-1">₹</span>
                                    <input
                                        type="number"
                                        value={editForm?.tax}
                                        onChange={(e) => setEditForm({ ...editForm, tax: parseFloat(e.target.value) || 0 })}
                                        className="text-2xl font-bold text-gray-900 dark:text-white bg-transparent border-b border-gray-300 dark:border-gray-600 w-full focus:outline-none"
                                    />
                                </div>
                            ) : (
                                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                                    ₹{expense.tax || '0.00'}
                                </p>
                            )}
                        </div>
                        <div className="bg-primary-50 dark:bg-gray-700 border-2 border-primary-100 dark:border-primary-900 p-4 rounded-lg">
                            <p className="text-sm text-primary-600 dark:text-primary-400">Total Amount</p>
                            <p className="text-2xl font-bold text-primary-900 dark:text-white">
                                ₹{isEditing ? (editForm?.total_amount?.toFixed(2) || '0.00') : (expense.total_amount || '0.00')}
                            </p>
                        </div>
                    </div>

                    <div className="mb-6">
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Items</h3>
                            {isEditing && (
                                <Button size="sm" variant="secondary" onClick={handleAddItem}>
                                    + Add Item
                                </Button>
                            )}
                        </div>

                        <div className="border dark:border-gray-700 rounded-lg overflow-hidden">
                            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                                <thead className="bg-gray-50 dark:bg-gray-700">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                            Item
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                            Quantity
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                            Price
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                                            Total
                                        </th>
                                        {isEditing && <th className="px-6 py-3"></th>}
                                    </tr>
                                </thead>
                                <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                                    {(isEditing ? editForm?.items : expense.items)?.map((item, idx) => (
                                        <tr key={idx}>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                                                {isEditing ? (
                                                    <input
                                                        type="text"
                                                        value={item.item_name}
                                                        onChange={(e) => handleItemChange(idx, 'item_name', e.target.value)}
                                                        className="border dark:border-gray-600 rounded px-2 py-1 w-full bg-transparent"
                                                        placeholder="Item name"
                                                    />
                                                ) : item.item_name}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-300">
                                                {isEditing ? (
                                                    <input
                                                        type="number"
                                                        min="1"
                                                        value={item.quantity}
                                                        onChange={(e) => handleItemChange(idx, 'quantity', parseInt(e.target.value) || 1)}
                                                        className="border dark:border-gray-600 rounded px-2 py-1 w-16 bg-transparent"
                                                    />
                                                ) : item.quantity}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-300">
                                                {isEditing ? (
                                                    <div className="flex items-center">
                                                        <span>₹</span>
                                                        <input
                                                            type="number"
                                                            min="0"
                                                            step="0.01"
                                                            value={item.price}
                                                            onChange={(e) => handleItemChange(idx, 'price', parseFloat(e.target.value) || 0)}
                                                            className="border dark:border-gray-600 rounded px-2 py-1 w-24 ml-1 bg-transparent"
                                                        />
                                                    </div>
                                                ) : `₹${item.price}`}
                                            </td>
                                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                                                ₹{(item.quantity * item.price).toFixed(2)}
                                            </td>
                                            {isEditing && (
                                                <td className="px-6 py-4 text-right">
                                                    <button
                                                        onClick={() => handleRemoveItem(idx)}
                                                        className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                                                    >
                                                        ✕
                                                    </button>
                                                </td>
                                            )}
                                        </tr>
                                    ))}
                                    {isEditing && editForm?.items?.length === 0 && (
                                        <tr>
                                            <td colSpan="5" className="px-6 py-4 text-center text-gray-500 dark:text-gray-400">
                                                No items. Click "Add Item" to add one.
                                            </td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>

                    {isEditing ? (
                        <div className="flex justify-end space-x-4 mt-8 pt-6 border-t dark:border-gray-700">
                            <Button variant="secondary" onClick={() => setIsEditing(false)}>
                                Cancel
                            </Button>
                            <Button onClick={handleSave} isLoading={updateMutation.isPending}>
                                Save Changes & Split Equally
                            </Button>
                        </div>
                    ) : (
                        expense.splits && expense.splits.length > 0 && (
                            <div>
                                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Split Details</h3>
                                <div className="space-y-3">
                                    {expense.splits.map((split, idx) => (
                                        <div key={idx} className="flex justify-between items-center p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                                            <div>
                                                <p className="font-medium text-gray-900 dark:text-white">{split.user_name}</p>
                                                <p className="text-sm text-gray-600 dark:text-gray-400">{split.user_email}</p>
                                            </div>
                                            <div className="text-right">
                                                <p className="font-semibold text-gray-900 dark:text-white">₹{split.amount}</p>
                                                <p className="text-xs text-gray-600 dark:text-gray-400">
                                                    {split.is_settled ? '✓ Settled' : 'Pending'}
                                                </p>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )
                    )}
                </div>
            </div>

            {expense.image_url && !isEditing && (
                <div className="bg-white dark:bg-gray-800 rounded-lg shadow dark:shadow-none dark:border dark:border-gray-700 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Original Bill Image</h3>
                    <img
                        src={expense.image_url}
                        alt="Bill"
                        className="max-w-full h-auto rounded-lg border dark:border-gray-700"
                    />
                </div>
            )}
        </Layout>
    );
};
