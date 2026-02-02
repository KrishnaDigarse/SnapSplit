import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation, useQuery } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import { expensesAPI } from '../../api/expenses';
import { Button } from '../common/Button';
import { Spinner } from '../common/Spinner';
import { ErrorMessage } from '../common/ErrorMessage';


export const BillUpload = ({ groupId, onSuccess, members = [] }) => {
    const [file, setFile] = useState(null);
    const [expenseId, setExpenseId] = useState(null);
    const [uploadStatus, setUploadStatus] = useState('idle'); // idle, uploading, processing, ready, failed
    const navigate = useNavigate();

    // Upload mutation
    const uploadMutation = useMutation({
        mutationFn: (file) => expensesAPI.uploadBill(groupId, file),
        onSuccess: (data) => {
            setExpenseId(data.id);
            setUploadStatus('processing');
        },
        onError: () => {
            setUploadStatus('failed');
            toast.error('Failed to upload bill image');
        }
    });

    // ... (keep poll status logic) ...

    // Poll status (only when processing)
    const { data: statusData } = useQuery({
        queryKey: ['expense-status', expenseId],
        queryFn: () => expensesAPI.pollExpenseStatus(expenseId),
        enabled: uploadStatus === 'processing' && !!expenseId,
        refetchInterval: (query) => {
            // Stop polling if status is not PROCESSING
            const currentStatus = query?.state?.data?.status;
            console.log('Polling status:', currentStatus);

            if (currentStatus && currentStatus !== 'PROCESSING') {
                console.log('Stopping poll - status is:', currentStatus);
                return false;
            }
            return 2000; // Poll every 2 seconds
        }
    });

    // Update status based on poll result
    useEffect(() => {
        console.log('Status data updated:', statusData);
        if (statusData) {
            if (statusData.status === 'READY') {
                console.log('Status is READY, redirecting...');
                setUploadStatus('ready');
                toast.success('Bill processed successfully!');
                // Small delay to show success message
                setTimeout(() => {
                    if (onSuccess) {
                        onSuccess(expenseId);
                    } else {
                        // Redirect to expense detail
                        navigate(`/expenses/${expenseId}`);
                    }
                }, 1500);
            } else if (statusData.status === 'FAILED') {
                console.log('Status is FAILED');
                setUploadStatus('failed');
                toast.error('Bill processing failed. Please try adding manually.');
            }
        }
    }, [statusData, expenseId, navigate, onSuccess]);

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            // Validate file type
            if (!selectedFile.type.startsWith('image/')) {
                alert('Please select an image file');
                return;
            }
            // Validate file size (max 10MB)
            if (selectedFile.size > 10 * 1024 * 1024) {
                alert('File size must be less than 10MB');
                return;
            }
            setFile(selectedFile);
        }
    };

    const handleUpload = () => {
        if (!file) return;
        setUploadStatus('uploading');
        uploadMutation.mutate(file);
    };

    const handleReset = () => {
        setFile(null);
        setExpenseId(null);
        setUploadStatus('idle');
    };

    return (
        <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow dark:shadow-none dark:border dark:border-gray-700">
            <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Upload Bill (AI Scanning)</h3>

            {uploadStatus === 'idle' && (
                <div>
                    <div className="mb-4">
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Select bill image
                        </label>
                        <input
                            type="file"
                            accept="image/*"
                            onChange={handleFileChange}
                            className="block w-full text-sm text-gray-500 dark:text-gray-400
                file:mr-4 file:py-2 file:px-4
                file:rounded-lg file:border-0
                file:text-sm file:font-semibold
                file:bg-primary-50 file:text-primary-700
                dark:file:bg-primary-900/30 dark:file:text-primary-300
                hover:file:bg-primary-100 dark:hover:file:bg-primary-900/50
                cursor-pointer"
                        />
                        {file && (
                            <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                                Selected: {file.name} ({(file.size / 1024).toFixed(1)} KB)
                            </p>
                        )}
                    </div>

                    <Button onClick={handleUpload} disabled={!file}>
                        Upload & Scan Bill
                    </Button>
                </div>
            )}

            {uploadStatus === 'uploading' && (
                <div className="text-center py-8">
                    <Spinner size="lg" text="Uploading bill..." />
                </div>
            )}

            {uploadStatus === 'processing' && (
                <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6 text-center">
                    <Spinner size="lg" />
                    <h4 className="mt-4 text-lg font-semibold text-blue-900 dark:text-blue-200">
                        🔄 Analyzing bill with AI...
                    </h4>
                    <p className="mt-2 text-sm text-blue-700 dark:text-blue-300">
                        This may take 5-10 seconds. We're extracting items, prices, and calculating totals.
                    </p>
                </div>
            )}

            {uploadStatus === 'ready' && (
                <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-6 text-center">
                    <svg className="mx-auto h-12 w-12 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                    <h4 className="mt-4 text-lg font-semibold text-green-900 dark:text-green-200">
                        ✅ Bill processed successfully!
                    </h4>
                    <p className="mt-2 text-sm text-green-700 dark:text-green-300">
                        Redirecting to expense details...
                    </p>
                </div>
            )}

            {uploadStatus === 'failed' && (
                <div>
                    <ErrorMessage
                        message="AI processing failed. The bill image may be unclear or the format is not supported."
                        action={
                            <div className="flex space-x-2">
                                <Button variant="secondary" size="sm" onClick={handleReset}>
                                    Try Another Image
                                </Button>
                                <Button size="sm" onClick={() => navigate(`/groups/${groupId}/expense/manual`)}>
                                    Add Manually
                                </Button>
                            </div>
                        }
                    />
                </div>
            )}
        </div>
    );
};
