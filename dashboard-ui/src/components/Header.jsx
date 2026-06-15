export default function Header() {
  return (
    <header className="w-full px-6 py-4 flex items-center justify-between border-b border-surface-200 bg-white/80 backdrop-blur-xl sticky top-0 z-30 shadow-sm shadow-surface-200/5">
      {/* Left: Logo + Title */}
      <div className="flex items-center gap-3.5">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-accent to-amber-500 flex items-center justify-center shadow-lg shadow-accent/20">
          <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 01-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 014.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0112 15a9.065 9.065 0 00-6.23.693L5 14.5m14.8.8l1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0112 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
          </svg>
        </div>
        <div>
          <h1 className="text-lg font-bold text-surface-900 tracking-tight">IMMBDA</h1>
          <p className="text-[11px] text-surface-400 font-bold tracking-wide uppercase">Prompt Logger System</p>
        </div>
      </div>

      {/* Right: Status + Avatar */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-green-500/10 border border-green-500/20">
          <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
          <span className="text-xs font-semibold text-green-600">Live</span>
        </div>
        <div className="w-8 h-8 rounded-full bg-gradient-to-br from-surface-200 to-surface-300 flex items-center justify-center ring-2 ring-surface-200">
          <svg className="w-4 h-4 text-surface-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z" />
          </svg>
        </div>
      </div>
    </header>
  );
}
