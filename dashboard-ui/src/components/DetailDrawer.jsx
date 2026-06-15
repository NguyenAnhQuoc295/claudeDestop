import { useState, useEffect } from 'react';
import { useEmployeeSessions } from '../hooks/useDashboard';

function formatTime(isoStr) {
  if (!isoStr) return '';
  try {
    const d = new Date(isoStr);
    return d.toLocaleString('vi-VN', {
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  } catch {
    return isoStr;
  }
}

function CategoryDot({ type }) {
  const colors = { chat: 'bg-blue-500', cowork: 'bg-purple-500', code: 'bg-emerald-500' };
  return <span className={`w-2 h-2 rounded-full ${colors[type] || 'bg-surface-400'} flex-shrink-0`} />;
}

function CategoryBadgeSmall({ type }) {
  const styles = {
    chat: 'badge-chat',
    cowork: 'badge-cowork',
    code: 'badge-code',
  };
  return <span className={styles[type] || 'badge'}>{type}</span>;
}

function SessionAccordion({ session }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="border border-surface-200 rounded-lg overflow-hidden transition-all shadow-sm">
      {/* Session Header */}
      <button
        className="accordion-header bg-surface-50/60 hover:bg-surface-100/40 w-full text-left"
        onClick={() => setOpen(!open)}
      >
        <div className="flex items-center gap-3 flex-1 min-w-0">
          <svg
            className={`w-4 h-4 text-surface-500 flex-shrink-0 transition-transform duration-200 ${open ? 'rotate-90' : ''}`}
            fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
          </svg>

          <div className="flex flex-col gap-0.5 min-w-0 flex-1">
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono text-surface-700 font-semibold truncate">{session.session_id.slice(0, 20)}…</span>
              <CategoryBadgeSmall type={session.category} />
            </div>
            <span className="text-[10px] text-surface-450">{session.project_name}</span>
          </div>
        </div>

        <div className="flex items-center gap-2 flex-shrink-0 ml-2">
          <span className="text-xs font-semibold text-surface-700 tabular-nums bg-surface-200/50 px-2 py-0.5 rounded">
            {session.prompt_count}
          </span>
        </div>
      </button>

      {/* Prompt List */}
      {open && (
        <div className="p-3 flex flex-col gap-2.5 bg-surface-100/10 animate-fade-in">
          {session.prompts.map((p, i) => (
            <div key={p.id || i} className="flex gap-3">
              {/* Timeline line */}
              <div className="flex flex-col items-center pt-1">
                <CategoryDot type={p.category} />
                {i < session.prompts.length - 1 && (
                  <div className="w-px flex-1 bg-surface-200 mt-1" />
                )}
              </div>
 
              {/* Prompt content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-[10px] text-surface-400 font-medium tabular-nums">{formatTime(p.created_at)}</span>
                  {p.hook_event && (
                    <span className="text-[10px] text-surface-450 font-mono">{p.hook_event}</span>
                  )}
                </div>
                <div className="prompt-bubble">
                  <p className="whitespace-pre-wrap break-words text-surface-800">{p.prompt}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function DetailDrawer({ email, employeeName, onClose }) {
  const { data, loading, error } = useEmployeeSessions(email);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (email) {
      requestAnimationFrame(() => setIsVisible(true));
    }
    return () => setIsVisible(false);
  }, [email]);

  const handleClose = () => {
    setIsVisible(false);
    setTimeout(onClose, 250);
  };

  if (!email) return null;

  return (
    <>
      {/* Overlay */}
      <div
        className={`drawer-overlay transition-opacity duration-300 ${isVisible ? 'opacity-100' : 'opacity-0'}`}
        onClick={handleClose}
      />

      {/* Drawer */}
      <aside
        className={`fixed top-0 right-0 h-full w-full sm:w-[480px] lg:w-[520px] bg-white/95 backdrop-blur-2xl border-l border-surface-200 z-50 flex flex-col shadow-2xl shadow-surface-300/40 transition-transform duration-300 ease-out ${isVisible ? 'translate-x-0' : 'translate-x-full'}`}
      >
        {/* Drawer Header */}
        <div className="p-5 border-b border-surface-200 flex items-start justify-between flex-shrink-0">
          <div className="flex items-center gap-3.5">
            <div className="w-11 h-11 rounded-xl bg-gradient-to-br from-accent/20 to-amber-500/15 flex items-center justify-center text-lg font-bold text-accent">
              {(employeeName || email.charAt(0)).charAt(0).toUpperCase()}
            </div>
            <div>
              <h2 className="text-base font-bold text-surface-900">{employeeName || email}</h2>
              <p className="text-xs text-surface-450 mt-0.5">{email}</p>
            </div>
          </div>
          <button
            id="drawer-close"
            onClick={handleClose}
            className="w-8 h-8 rounded-lg flex items-center justify-center text-surface-500 hover:text-surface-800 hover:bg-surface-100 transition-all"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Session count badge */}
        {data && (
          <div className="px-5 py-3 border-b border-surface-200 flex items-center gap-2">
            <svg className="w-4 h-4 text-surface-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 12h16.5m-16.5 3.75h16.5M3.75 19.5h16.5M5.625 4.5h12.75a1.875 1.875 0 010 3.75H5.625a1.875 1.875 0 010-3.75z" />
            </svg>
            <span className="text-xs text-surface-500">
              <span className="font-semibold text-surface-800">{data.sessions?.length || 0}</span> sessions found
            </span>
          </div>
        )}

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-5">
          {loading && (
            <div className="flex flex-col gap-3">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="shimmer h-16 rounded-lg" />
              ))}
            </div>
          )}

          {error && (
            <div className="text-center py-12">
              <div className="w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
                </svg>
              </div>
              <p className="text-sm text-red-400 font-medium">Failed to load sessions</p>
              <p className="text-xs text-surface-500 mt-1">{error}</p>
            </div>
          )}

          {data && !loading && data.sessions?.length === 0 && (
            <div className="text-center py-12">
              <div className="w-12 h-12 rounded-full bg-surface-100 flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6 text-surface-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M20.25 7.5l-.625 10.632a2.25 2.25 0 01-2.247 2.118H6.622a2.25 2.25 0 01-2.247-2.118L3.75 7.5m6 4.125l2.25 2.25m0 0l2.25 2.25M12 13.875l2.25-2.25M12 13.875l-2.25 2.25M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z" />
                </svg>
              </div>
              <p className="text-sm text-surface-500">No sessions found</p>
            </div>
          )}

          {data && !loading && data.sessions?.length > 0 && (
            <div className="flex flex-col gap-3">
              {data.sessions.map((session, i) => (
                <SessionAccordion key={session.session_id || i} session={session} />
              ))}
            </div>
          )}
        </div>
      </aside>
    </>
  );
}
