import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './context/AuthContext';
import { FullPageSpinner } from './components/common/Spinner';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Dashboard } from './pages/Dashboard';
import { Friends } from './pages/Friends';
import { Groups } from './pages/Groups';
import { GroupDetail } from './pages/GroupDetail';
import { ExpenseDetail } from './pages/ExpenseDetail';
import './index.css';

const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            refetchOnWindowFocus: false,
            retry: 1
        }
    }
});

const ProtectedRoute = ({ children }) => {
    const { isAuthenticated, loading } = useAuth();

    if (loading) {
        return <FullPageSpinner />;
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" />;
    }

    return children;
};

const AppRoutes = () => {
    const { isAuthenticated, loading } = useAuth();

    if (loading) {
        return <FullPageSpinner />;
    }

    return (
        <Routes>
            <Route path="/login" element={isAuthenticated ? <Navigate to="/dashboard" /> : <Login />} />
            <Route path="/register" element={isAuthenticated ? <Navigate to="/dashboard" /> : <Register />} />

            <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/friends" element={<ProtectedRoute><Friends /></ProtectedRoute>} />
            <Route path="/groups" element={<ProtectedRoute><Groups /></ProtectedRoute>} />
            <Route path="/groups/:groupId" element={<ProtectedRoute><GroupDetail /></ProtectedRoute>} />
            <Route path="/expenses/:expenseId" element={<ProtectedRoute><ExpenseDetail /></ProtectedRoute>} />

            <Route path="/" element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} />} />
        </Routes>
    );
};

function App() {
    return (
        <QueryClientProvider client={queryClient}>
            <BrowserRouter>
                <AuthProvider>
                    <AppRoutes />
                </AuthProvider>
            </BrowserRouter>
        </QueryClientProvider>
    );
}

export default App;
