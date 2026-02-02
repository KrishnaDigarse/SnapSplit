import { createContext, useState, useEffect, useContext } from 'react';
import { toast } from 'react-hot-toast';
import { authAPI } from '../api/auth';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check if token exists and fetch user
        const token = localStorage.getItem('access_token');
        if (token) {
            authAPI.getCurrentUser()
                .then(setUser)
                .catch(() => {
                    localStorage.removeItem('access_token');
                })
                .finally(() => setLoading(false));
        } else {
            setLoading(false);
        }
    }, []);

    const login = async (email, password) => {
        try {
            const { access_token } = await authAPI.login(email, password);
            localStorage.setItem('access_token', access_token);
            const userData = await authAPI.getCurrentUser();
            setUser(userData);
            toast.success('Welcome back!');
        } catch (error) {
            toast.error(error.response?.data?.detail || 'Login failed');
            throw error;
        }
    };

    const register = async (email, password, name) => {
        try {
            await authAPI.register(email, password, name);
            toast.success('Registration successful! Logging in...');
            // Auto-login after registration
            await login(email, password);
        } catch (error) {
            toast.error(error.response?.data?.detail || 'Registration failed');
            throw error;
        }
    };

    const logout = () => {
        localStorage.removeItem('access_token');
        setUser(null);
        window.location.href = '/login';
    };

    return (
        <AuthContext.Provider value={{
            user,
            isAuthenticated: !!user,
            login,
            register,
            logout,
            loading
        }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within AuthProvider');
    }
    return context;
};
