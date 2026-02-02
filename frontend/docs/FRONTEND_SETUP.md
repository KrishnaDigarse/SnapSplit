# SnapSplit Frontend - Setup Guide

## 📋 Prerequisites

- Node.js 18+ and npm
- Backend server running on `http://localhost:8000`

---

## 🚀 Installation

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Environment Setup

The frontend is configured to connect to the backend at `http://localhost:8000` by default (via Vite proxy).

If your backend runs on a different port, update `vite.config.js`:

```javascript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:YOUR_PORT',  // Change this
        changeOrigin: true
      }
    }
  }
})
```

---

## 🏃 Running the Development Server

```bash
npm run dev
```

The app will be available at **http://localhost:3000**

---

## 🏗️ Building for Production

```bash
npm run build
```

Build output will be in the `dist/` directory.

To preview the production build:

```bash
npm run preview
```

---

## 📁 Project Structure

```
frontend/
├── src/
│   ├── api/              # API client and endpoint modules
│   │   ├── client.js     # Axios instance with interceptors
│   │   ├── auth.js       # Authentication endpoints
│   │   ├── friends.js    # Friends management
│   │   ├── groups.js     # Groups management
│   │   └── expenses.js   # Expenses & bill upload
│   ├── components/
│   │   ├── common/       # Reusable UI components
│   │   ├── layout/       # Layout components (Navbar, Layout)
│   │   └── expense/      # Expense-specific components (BillUpload)
│   ├── pages/            # Page components
│   ├── context/          # React contexts (AuthContext)
│   ├── App.jsx           # Main app with routing
│   └── main.jsx          # Entry point
├── public/               # Static assets
├── index.html            # HTML template
├── vite.config.js        # Vite configuration
├── tailwind.config.js    # Tailwind CSS configuration
└── package.json          # Dependencies
```

---

## 🔑 Key Features

### Authentication
- JWT-based authentication
- Token stored in localStorage
- Auto-redirect on 401 errors
- Protected routes

### Async Bill Upload
- Upload bill image
- Real-time status polling with React Query
- Visual feedback for all states (uploading, processing, ready, failed)
- Automatic redirect on success

### Friends & Groups
- Send/accept/reject friend requests
- Create and manage groups
- View group balances and expenses

---

## 🛠️ Tech Stack

- **React 18** - UI library
- **Vite** - Build tool
- **React Router v6** - Routing
- **React Query** - Data fetching & caching
- **Axios** - HTTP client
- **Tailwind CSS** - Styling
- **React Hot Toast** - Notifications

---

## 🐛 Troubleshooting

### Backend Connection Issues

**Problem:** API calls fail with network errors

**Solution:**
1. Ensure backend is running on `http://localhost:8000`
2. Check Vite proxy configuration in `vite.config.js`
3. Check browser console for CORS errors

### Authentication Issues

**Problem:** User gets logged out unexpectedly

**Solution:**
1. Check if backend JWT token is valid
2. Clear localStorage: `localStorage.clear()`
3. Re-login

### Build Errors

**Problem:** `npm run build` fails

**Solution:**
1. Delete `node_modules` and `package-lock.json`
2. Run `npm install` again
3. Ensure Node.js version is 18+

---

## 📝 Development Tips

### Hot Module Replacement (HMR)

Vite provides instant HMR. Changes to components will reflect immediately without full page reload.

### React Query DevTools

To enable React Query DevTools for debugging:

```bash
npm install @tanstack/react-query-devtools
```

Then add to `App.jsx`:

```javascript
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

// Inside QueryClientProvider
<ReactQueryDevtools initialIsOpen={false} />
```

### Tailwind CSS IntelliSense

Install the Tailwind CSS IntelliSense VS Code extension for autocomplete.

---

## 🚀 Next Steps

1. **Test the async bill upload flow**
2. **Customize Tailwind theme** in `tailwind.config.js`
3. **Add more features** (settlements, notifications, etc.)
4. **Deploy to production** (Vercel, Netlify, etc.)

---

## 📚 Additional Resources

- [React Documentation](https://react.dev)
- [Vite Documentation](https://vitejs.dev)
- [React Query Documentation](https://tanstack.com/query)
- [Tailwind CSS Documentation](https://tailwindcss.com)
