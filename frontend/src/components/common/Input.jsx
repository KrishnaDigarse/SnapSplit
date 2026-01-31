export const Input = ({
    label,
    type = 'text',
    name,
    value,
    onChange,
    error,
    placeholder,
    required = false,
    disabled = false
}) => {
    return (
        <div className="mb-4">
            {label && (
                <label htmlFor={name} className="block text-sm font-medium text-gray-700 mb-1">
                    {label} {required && <span className="text-red-500">*</span>}
                </label>
            )}
            <input
                type={type}
                id={name}
                name={name}
                value={value}
                onChange={onChange}
                placeholder={placeholder}
                required={required}
                disabled={disabled}
                className={`w-full px-3 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 ${error ? 'border-red-500' : 'border-gray-300'
                    } ${disabled ? 'bg-gray-100 cursor-not-allowed' : ''}`}
            />
            {error && (
                <p className="mt-1 text-sm text-red-600">{error}</p>
            )}
        </div>
    );
};
