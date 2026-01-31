import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Button } from '../common/Button';

export const Navbar = () => {
    const { user, isAuthenticated, logout } = useAuth();

    return (
        <nav className="bg-white shadow-sm border-b">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                <div className="flex justify-between h-16">
                    <div className="flex items-center">
                        <Link to="/" className="text-2xl font-bold text-primary-600">
                            SnapSplit
                        </Link>
                        {isAuthenticated && (
                            <div className="ml-10 flex space-x-4">
                                <Link to="/dashboard" className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium">
                                    Dashboard
                                </Link>
                                <Link to="/friends" className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium">
                                    Friends
                                </Link>
                                <Link to="/groups" className="text-gray-700 hover:text-primary-600 px-3 py-2 rounded-md text-sm font-medium">
                                    Groups
                                </Link>
                            </div>
                        )}
                    </div>
                    <div className="flex items-center">
                        {isAuthenticated ? (
                            <div className="flex items-center space-x-4">
                                <span className="text-sm text-gray-700">
                                    {user?.name || user?.email}
                                </span>
                                <Button variant="outline" size="sm" onClick={logout}>
                                    Logout
                                </Button>
                            </div>
                        ) : (
                            <div className="flex space-x-2">
                                <Link to="/login">
                                    <Button variant="outline" size="sm">Login</Button>
                                </Link>
                                <Link to="/register">
                                    <Button size="sm">Sign Up</Button>
                                </Link>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </nav>
    );
};
