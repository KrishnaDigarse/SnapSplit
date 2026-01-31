import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { expensesAPI } from '../api/expenses';
import { Layout } from '../components/layout/Layout';
import { Spinner } from '../components/common/Spinner';
import { ErrorMessage } from '../components/common/ErrorMessage';
import { Button } from '../components/common/Button';

export const ExpenseDetail = () => {
    const { expenseId } = useParams();

    const { data: expense, isLoading } = useQuery({
        queryKey: ['expenses', expenseId],
        queryFn: () => expensesAPI.getExpenseDetail(expenseId)
    });

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
            <div className="mb-6">
                <Link to={`/groups/${expense.group_id}`} className="text-primary-600 hover:text-primary-700 text-sm">
                    ← Back to Group
                </Link>
            </div>

            <div className="bg-white rounded-lg shadow mb-6">
                <div className="px-6 py-4 border-b">
                    <div className="flex justify-between items-start">
                        <div>
                            <h1 className="text-2xl font-bold text-gray-900">
                                {expense.description || 'Expense Details'}
                            </h1>
                            <p className="text-sm text-gray-600 mt-1">
                                Created on {new Date(expense.created_at).toLocaleDateString()}
                            </p>
                        </div>
                        <div className="flex items-center space-x-2">
                            <span className={`px-3 py-1 text-sm rounded-full ${statusColors[expense.status]}`}>
                                {expense.status}
                            </span>
                            {expense.source_type === 'BILL_IMAGE' && (
                                <span className="px-3 py-1 text-sm bg-primary-100 text-primary-800 rounded-full">
                                    🤖 AI Scanned
                                </span>
                            )}
                        </div>
                    </div>
                </div>

                {expense.status === 'FAILED' && (
                    <div className="p-6 border-b">
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
                        <div className="bg-gray-50 p-4 rounded-lg">
                            <p className="text-sm text-gray-600">Subtotal</p>
                            <p className="text-2xl font-bold text-gray-900">
                                ₹{expense.subtotal || '0.00'}
                            </p>
                        </div>
                        <div className="bg-gray-50 p-4 rounded-lg">
                            <p className="text-sm text-gray-600">Tax</p>
                            <p className="text-2xl font-bold text-gray-900">
                                ₹{expense.tax || '0.00'}
                            </p>
                        </div>
                        <div className="bg-primary-50 p-4 rounded-lg">
                            <p className="text-sm text-primary-600">Total Amount</p>
                            <p className="text-2xl font-bold text-primary-900">
                                ₹{expense.total_amount || '0.00'}
                            </p>
                        </div>
                    </div>

                    {expense.items && expense.items.length > 0 && (
                        <div className="mb-6">
                            <h3 className="text-lg font-semibold text-gray-900 mb-4">Items</h3>
                            <div className="border rounded-lg overflow-hidden">
                                <table className="min-w-full divide-y divide-gray-200">
                                    <thead className="bg-gray-50">
                                        <tr>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Item
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Quantity
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Price
                                            </th>
                                            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                                Total
                                            </th>
                                        </tr>
                                    </thead>
                                    <tbody className="bg-white divide-y divide-gray-200">
                                        {expense.items.map((item, idx) => (
                                            <tr key={idx}>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                                                    {item.item_name}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                                                    {item.quantity}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                                                    ₹{item.price}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                                                    ₹{(item.quantity * item.price).toFixed(2)}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}

                    {expense.splits && expense.splits.length > 0 && (
                        <div>
                            <h3 className="text-lg font-semibold text-gray-900 mb-4">Split Details</h3>
                            <div className="space-y-3">
                                {expense.splits.map((split, idx) => (
                                    <div key={idx} className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                                        <div>
                                            <p className="font-medium text-gray-900">{split.user_name}</p>
                                            <p className="text-sm text-gray-600">{split.user_email}</p>
                                        </div>
                                        <div className="text-right">
                                            <p className="font-semibold text-gray-900">₹{split.amount}</p>
                                            <p className="text-xs text-gray-600">
                                                {split.is_settled ? '✓ Settled' : 'Pending'}
                                            </p>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {expense.image_url && (
                <div className="bg-white rounded-lg shadow p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Original Bill Image</h3>
                    <img
                        src={expense.image_url}
                        alt="Bill"
                        className="max-w-full h-auto rounded-lg border"
                    />
                </div>
            )}
        </Layout>
    );
};
