import { useState, useMemo } from 'react';

const FILTERS = [
  { key: 'all', label: 'All', activeClass: 'bg-surface-800 text-white border-surface-700' },
  { key: 'chat', label: 'Chat', activeClass: 'bg-blue-100 text-blue-700 border-blue-200' },
  { key: 'cowork', label: 'Cowork', activeClass: 'bg-purple-100 text-purple-700 border-purple-200' },
  { key: 'code', label: 'Code', activeClass: 'bg-emerald-100 text-emerald-700 border-emerald-200' },
];

function CategoryBadge({ type, value }) {
  const styles = {
    chat: 'badge-chat',
    cowork: 'badge-cowork',
    code: 'badge-code',
  };
  return (
    <span className={styles[type] || 'badge'}>
      {value}
    </span>
  );
}

export default function EmployeeTable({ employees = [], selectedEmail, onSelectEmployee }) {
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');

  const filtered = useMemo(() => {
    let result = employees;

    // Search filter
    if (search.trim()) {
      const q = search.toLowerCase();
      result = result.filter(e =>
        e.name.toLowerCase().includes(q) || e.email.toLowerCase().includes(q)
      );
    }

    // Category filter
    if (filter !== 'all') {
      result = result.filter(e => (e[filter] || 0) > 0);
    }

    return result;
  }, [employees, search, filter]);

  return (
    <div className="glass-card flex flex-col animate-fade-in" style={{ animationDelay: '0.25s' }}>
      {/* Toolbar */}
      <div className="p-4 border-b border-surface-200 flex flex-col sm:flex-row gap-3 sm:items-center sm:justify-between">
        {/* Search */}
        <div className="relative flex-1 max-w-md">
          <svg
            className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400"
            fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
          </svg>
          <input
            id="employee-search"
            type="text"
            placeholder="Search by name or email…"
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full pl-9 pr-4 py-2 rounded-lg bg-white border border-surface-200 text-sm text-surface-850 placeholder-surface-400 focus:outline-none focus:border-accent/60 focus:ring-1 focus:ring-accent/20 transition-all shadow-sm"
          />
        </div>

        {/* Filter buttons */}
        <div className="flex items-center gap-2">
          {FILTERS.map(f => (
            <button
              key={f.key}
              id={`filter-${f.key}`}
              onClick={() => setFilter(f.key)}
              className={filter === f.key ? `filter-btn-active ${f.activeClass}` : 'filter-btn-inactive'}
            >
              {f.label}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto flex-1">
        <table className="w-full">
          <thead>
            <tr className="border-b border-surface-200">
              <th className="text-left px-4 py-3 text-xs font-bold text-surface-500 uppercase tracking-wider">Employee</th>
              <th className="text-center px-3 py-3 text-xs font-bold text-surface-500 uppercase tracking-wider">Total</th>
              <th className="text-center px-3 py-3 text-xs font-bold text-surface-500 uppercase tracking-wider">
                <span className="text-blue-600">Chat</span>
              </th>
              <th className="text-center px-3 py-3 text-xs font-bold text-surface-500 uppercase tracking-wider">
                <span className="text-purple-600">Cowork</span>
              </th>
              <th className="text-center px-3 py-3 text-xs font-bold text-surface-500 uppercase tracking-wider">
                <span className="text-emerald-600">Code</span>
              </th>
              <th className="text-center px-3 py-3 text-xs font-bold text-surface-500 uppercase tracking-wider">Sessions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-surface-200/40">
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-12 text-center text-surface-400 text-sm">
                  <div className="flex flex-col items-center gap-2">
                    <svg className="w-8 h-8 text-surface-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M15.182 16.318A4.486 4.486 0 0012.016 15a4.486 4.486 0 00-3.198 1.318M21 12a9 9 0 11-18 0 9 9 0 0118 0zM9.75 9.75c0 .414-.168.75-.375.75S9 10.164 9 9.75 9.168 9 9.375 9s.375.336.375.75zm-.375 0h.008v.015h-.008V9.75zm5.625 0c0 .414-.168.75-.375.75s-.375-.336-.375-.75.168-.75.375-.75.375.336.375.75zm-.375 0h.008v.015h-.008V9.75z" />
                    </svg>
                    <span>No employees found</span>
                  </div>
                </td>
              </tr>
            ) : (
              filtered.map((emp, i) => (
                <tr
                  key={emp.email}
                  id={`employee-row-${i}`}
                  onClick={() => onSelectEmployee(emp.email)}
                  className={`table-row-hover ${selectedEmail === emp.email ? 'bg-accent/10 border-l-2 border-l-accent' : ''}`}
                >
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-accent/25 to-amber-500/20 flex items-center justify-center text-xs font-bold text-accent flex-shrink-0">
                        {emp.name.charAt(0).toUpperCase()}
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-semibold text-surface-800 truncate">{emp.name}</p>
                        <p className="text-xs text-surface-450 truncate">{emp.email}</p>
                      </div>
                    </div>
                  </td>
                  <td className="text-center px-3 py-3">
                    <span className="text-sm font-bold text-surface-800 tabular-nums">{emp.total}</span>
                  </td>
                  <td className="text-center px-3 py-3">
                    <CategoryBadge type="chat" value={emp.chat || 0} />
                  </td>
                  <td className="text-center px-3 py-3">
                    <CategoryBadge type="cowork" value={emp.cowork || 0} />
                  </td>
                  <td className="text-center px-3 py-3">
                    <CategoryBadge type="code" value={emp.code || 0} />
                  </td>
                  <td className="text-center px-3 py-3">
                    <span className="text-xs text-surface-500 tabular-nums">{emp.session_count || 0}</span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Footer */}
      <div className="px-4 py-2.5 border-t border-surface-200 text-xs text-surface-400">
        Showing {filtered.length} of {employees.length} members
      </div>
    </div>
  );
}
