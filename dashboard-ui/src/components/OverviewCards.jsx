import DonutChart from './DonutChart';

function KpiCard({ label, value, icon, gradient, delay = '0s' }) {
  return (
    <div
      className="kpi-card animate-fade-in group"
      style={{ animationDelay: delay }}
    >
      {/* Top gradient bar */}
      <div className={`absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r ${gradient} opacity-60 group-hover:opacity-100 transition-opacity`} />

      <div className="flex items-start justify-between">
        <div className="flex flex-col gap-1">
          <span className="text-xs font-semibold text-surface-500 uppercase tracking-wider">{label}</span>
          <span className="text-2xl font-bold text-surface-900 tabular-nums">{value.toLocaleString()}</span>
        </div>
        <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${gradient} flex items-center justify-center opacity-20 group-hover:opacity-30 transition-opacity`}>
          {icon}
        </div>
      </div>
    </div>
  );
}

export default function OverviewCards({ summary }) {
  if (!summary) return null;

  return (
    <div className="flex flex-col gap-5 lg:flex-row lg:items-stretch">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 flex-1">
        <KpiCard
          label="Total Prompts"
          value={summary.total_prompts || 0}
          gradient="from-accent to-indigo-400"
          delay="0.05s"
          icon={
            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.087.16 2.185.283 3.293.369V21l4.076-4.076a1.526 1.526 0 011.037-.443 48.282 48.282 0 005.68-.494c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z" />
            </svg>
          }
        />
        <KpiCard
          label="Active Members"
          value={summary.unique_employees || 0}
          gradient="from-cyan-500 to-blue-500"
          delay="0.1s"
          icon={
            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
            </svg>
          }
        />
        <KpiCard
          label="Projects"
          value={summary.unique_projects || 0}
          gradient="from-emerald-500 to-green-500"
          delay="0.15s"
          icon={
            <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 12.75V12A2.25 2.25 0 014.5 9.75h15A2.25 2.25 0 0121.75 12v.75m-8.69-6.44l-2.12-2.12a1.5 1.5 0 00-1.061-.44H4.5A2.25 2.25 0 002.25 6v12a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9a2.25 2.25 0 00-2.25-2.25h-5.379a1.5 1.5 0 01-1.06-.44z" />
            </svg>
          }
        />
      </div>

      {/* Donut Chart */}
      <div className="glass-card p-5 flex items-center animate-fade-in" style={{ animationDelay: '0.2s' }}>
        <DonutChart categories={summary.categories || {}} />
      </div>
    </div>
  );
}
