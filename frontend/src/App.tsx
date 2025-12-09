import { useEffect, useState } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import { useFamilyStore } from './store/familyStore';
import { useNotificationsStore } from './store/notificationsStore';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Children from './pages/Children';
import Settings from './pages/Settings';
import Wishlist from './pages/Wishlist';
import Letters from './pages/Letters';
import GoodDeeds from './pages/GoodDeeds';
import Sidebar from './components/Sidebar';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuthStore();

  if (isLoading) {
    return (
      <div className="loading-screen">
        <div className="logo-icon">🎅</div>
        <div className="spinner" />
        <p style={{ color: 'var(--text-secondary)' }}>Loading Santa's Workshop...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

function AppLayout({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { fetchFamily } = useFamilyStore();
  const { fetchUnreadCount } = useNotificationsStore();

  useEffect(() => {
    fetchFamily();
    fetchUnreadCount();
  }, [fetchFamily, fetchUnreadCount]);

  return (
    <div className="app-layout">
      <button
        className="mobile-menu-btn"
        onClick={() => setSidebarOpen(true)}
      >
        ☰
      </button>
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <main className="main-content">
        {children}
      </main>
    </div>
  );
}

// Placeholder pages
function PlaceholderPage({ title, icon }: { title: string; icon: string }) {
  return (
    <div className="page-content">
      <div className="page-header" style={{ marginBottom: 32, padding: 0, border: 'none', background: 'transparent' }}>
        <h1 className="page-title">
          <span className="title-icon">{icon}</span>
          {title}
        </h1>
      </div>
      <div className="card">
        <div className="card-body">
          <div className="empty-state">
            <div className="empty-state-icon">{icon}</div>
            <h3>Coming Soon!</h3>
            <p>This page is under construction in Santa's Workshop.</p>
          </div>
        </div>
      </div>
    </div>
  );
}

function App() {
  const { checkAuth, isAuthenticated } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  return (
    <Routes>
      <Route
        path="/login"
        element={isAuthenticated ? <Navigate to="/" replace /> : <Login />}
      />
      <Route
        path="/register"
        element={isAuthenticated ? <Navigate to="/" replace /> : <Register />}
      />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Dashboard />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/children"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Children />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/wishlist"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Wishlist />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/letters"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Letters />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/timeline"
        element={
          <ProtectedRoute>
            <AppLayout>
              <PlaceholderPage title="Scrapbook" icon="📖" />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/deeds"
        element={
          <ProtectedRoute>
            <AppLayout>
              <GoodDeeds />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/moderation"
        element={
          <ProtectedRoute>
            <AppLayout>
              <PlaceholderPage title="Moderation" icon="🛡️" />
            </AppLayout>
          </ProtectedRoute>
        }
      />
      <Route
        path="/settings"
        element={
          <ProtectedRoute>
            <AppLayout>
              <Settings />
            </AppLayout>
          </ProtectedRoute>
        }
      />
    </Routes>
  );
}

export default App;
