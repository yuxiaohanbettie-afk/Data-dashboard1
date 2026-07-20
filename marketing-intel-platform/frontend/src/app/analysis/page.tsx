export default function AnalysisPage() {
  return (
    <div className="p-6 md:p-8">
      <div className="text-sm text-zinc-500">分析</div>
      <h1 className="mt-1 text-2xl font-semibold tracking-tight">Analysis Workspace</h1>

      <div className="mt-6 rounded-xl border border-zinc-200 bg-white p-4 text-sm text-zinc-600 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-300">
        这里会逐步补齐：Country / Industry / Ad Type / Campaign / Trend / Platform Comparison 等页面。
        目前后端已提供 KPI 对比与异常列表接口，前端先以首页 + Upload Center 打通“导入→入库→查询”闭环。
      </div>
    </div>
  );
}

