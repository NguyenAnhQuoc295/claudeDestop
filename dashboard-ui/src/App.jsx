import { useState } from 'react';
import Header from './components/Header';
import OverviewCards from './components/OverviewCards';
import EmployeeTable from './components/EmployeeTable';
import DetailDrawer from './components/DetailDrawer';
import { useDashboard } from './hooks/useDashboard';

export default function App() {
  const { summary, loading, error, refetch } = useDashboard();
  const [selectedEmail, setSelectedEmail] = useState(null);

  const selectedEmployee = summary?.employees?.find(e => e.email === selectedEmail);

  const handleSelectEmployee = (email) => {
    setSelectedEmail(prev => prev === email ? null : email);
  };

  return (
    <div className="min-h-screen bg-surface-50 flex flex-col">
      <Header />

      <main className="flex-1 p-6 flex flex-col gap-6 max-w-[1600px] mx-auto w-full">
        {/* Error State */}
        {error && (
          <div className="glass-card p-6 border-red-500/20 bg-red-500/5">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-red-500/10 flex items-center justify-center flex-shrink-0">
                <svg className="w-5 h-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-red-400">Connection Error</p>
                <p className="text-xs text-surface-400 mt-0.5">Unable to connect to the API server. Make sure the backend is running on port 8000.</p>
              </div>
              <button
                onClick={refetch}
                className="ml-auto px-4 py-2 rounded-lg bg-red-500/10 text-red-400 text-xs font-medium hover:bg-red-500/20 transition-colors border border-red-500/20"
              >
                Retry
              </button>
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading && !summary && (
          <div className="flex flex-col gap-6">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="shimmer h-24 rounded-xl" />
              ))}
            </div>
            <div className="shimmer h-96 rounded-xl" />
          </div>
        )}

        {/* Content */}
        {summary && (
          <>
            {/* Overview Section */}
            <OverviewCards summary={summary} />

            {/* Employee Table */}
            <EmployeeTable
              employees={summary.employees || []}
              selectedEmail={selectedEmail}
              onSelectEmployee={handleSelectEmployee}
            />
          </>
        )}
      </main>

      {/* Detail Drawer */}
      <DetailDrawer
        email={selectedEmail}
        employeeName={selectedEmployee?.name}
        onClose={() => setSelectedEmail(null)}
      />
    </div>
  );
}
