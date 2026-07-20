"use client";

import { useEffect, useMemo, useState } from "react";
import { KpiCard } from "@/components/KpiCard";
import { apiGet } from "@/lib/api";

type KPI = {
  spend_usd: number;
  gmv: number;
  roas: number | null;
  orders: number;
  ctr: number | null;
  cpa: number | null;
  cpc: number | null;
};

type KPICompareResponse = {
  current: KPI;
  previous: KPI;
  diff_pct: Record<string, number | null>;
};

type Anomaly = {
  id: number;
  dt: string;
  dimension: string;
  metric: string;
  severity: string;
  delta_pct: number | null;
};

function fmtMoney(v: number) {
  return v.toLocaleString(undefined, { maximumFractionDigits: 2 });
}

export default function Home() {
  const [platform, setPlatform] = useState<"google" | "meta" | "all">("all");
  const [loading, setLoading] = useState(true);
  const [err, setErr] = useState<string | null>(null);
  const [kpi, setKpi] = useState<KPICompareResponse | null>(null);
  const [alerts, setAlerts] = useState<Anomaly[]>([]);

  const today = useMemo(() => new Date(), []);
  const ranges = useMemo(() => {
    const end = new Date(today);
    const curEnd = new Date(end);
    const curStart = new Date(end);
    curStart.setDate(curStart.getDate() - 6); // 7 days
    const prevEnd = new Date(curStart);
    prevEnd.setDate(prevEnd.getDate() - 1);
    const prevStart = new Date(prevEnd);
    prevStart.setDate(prevStart.getDate() - 6);
    const iso = (d: Date) => d.toISOString().slice(0, 10);
    return {
      current_start: iso(curStart),
      current_end: iso(curEnd),
      previous_start: iso(prevStart),
      previous_end: iso(prevEnd),
    };
  }, [today]);

  useEffect(() => {
    let cancelled = false;
    async function run() {
      setLoading(true);
      setErr(null);
      try {
        const qp = new URLSearchParams(ranges);
        if (platform !== "all") qp.set("platform", platform);
        const data = await apiGet<KPICompareResponse>(`/metrics/kpi_compare?${qp.toString()}`);
        const a = await apiGet<Anomaly[]>(`/anomalies?limit=10`);
        if (cancelled) return;
        setKpi(data);
        setAlerts(a);
      } catch (e) {
        if (cancelled) return;
        setErr(e instanceof Error ? e.message : String(e));
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    void run();
    return () => {
      cancelled = true;
    };
  }, [platform, ranges]);

  return (
    <div className="p-6 md:p-8">
      <div className="flex items-center justify-between gap-4">
        <div>
          <div className="text-sm text-zinc-500">首页</div>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight">KPI 总览</h1>
        </div>
        <div className="flex items-center gap-2">
          <select
            className="h-10 rounded-lg border border-zinc-200 bg-white px-3 text-sm dark:border-zinc-800 dark:bg-zinc-950"
            value={platform}
            onChange={(e) => setPlatform(e.target.value as any)}
          >
            <option value="all">全部平台</option>
            <option value="google">Google</option>
            <option value="meta">Meta</option>
          </select>
          <a
            className="h-10 inline-flex items-center rounded-lg bg-zinc-900 px-3 text-sm text-white hover:bg-zinc-800 dark:bg-white dark:text-zinc-900 dark:hover:bg-zinc-100"
            href="/upload"
          >
            导入 Excel
          </a>
        </div>
      </div>

      <div className="mt-3 text-xs text-zinc-500">
        当前周期：{ranges.current_start} ~ {ranges.current_end}；对比：{ranges.previous_start} ~{" "}
        {ranges.previous_end}
      </div>

      {err ? (
        <div className="mt-6 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700 dark:border-rose-900/50 dark:bg-rose-950/30 dark:text-rose-200">
          后端未连接或无数据：{err}
          <div className="mt-2 text-xs opacity-80">
            请先启动后端 `uvicorn app.main:app --reload --port 8000`，然后到 Upload Center 导入 Excel。
          </div>
        </div>
      ) : null}

      <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiCard
          title="Spend (USD)"
          value={loading || !kpi ? "—" : fmtMoney(kpi.current.spend_usd)}
          diffPct={kpi?.diff_pct?.spend_usd ?? null}
        />
        <KpiCard
          title="GMV"
          value={loading || !kpi ? "—" : fmtMoney(kpi.current.gmv)}
          diffPct={kpi?.diff_pct?.gmv ?? null}
        />
        <KpiCard
          title="ROAS"
          value={loading || !kpi || kpi.current.roas == null ? "—" : kpi.current.roas.toFixed(2)}
          diffPct={kpi?.diff_pct?.roas ?? null}
        />
        <KpiCard
          title="Orders"
          value={loading || !kpi ? "—" : fmtMoney(kpi.current.orders)}
          diffPct={kpi?.diff_pct?.orders ?? null}
        />
        <KpiCard
          title="CTR"
          value={loading || !kpi || kpi.current.ctr == null ? "—" : `${(kpi.current.ctr * 100).toFixed(2)}%`}
          diffPct={kpi?.diff_pct?.ctr ?? null}
        />
        <KpiCard
          title="CPA (USD)"
          value={loading || !kpi || kpi.current.cpa == null ? "—" : fmtMoney(kpi.current.cpa)}
          diffPct={kpi?.diff_pct?.cpa ?? null}
        />
        <KpiCard
          title="CPC (USD)"
          value={loading || !kpi || kpi.current.cpc == null ? "—" : fmtMoney(kpi.current.cpc)}
          diffPct={kpi?.diff_pct?.cpc ?? null}
        />
        <KpiCard title="数据" value={loading ? "加载中…" : "OK"} diffPct={null} />
      </div>

      <div className="mt-8">
        <div className="text-sm font-semibold">Alerts</div>
        <div className="mt-3 space-y-2">
          {alerts.length === 0 ? (
            <div className="text-sm text-zinc-500">暂无异常（或尚未导入数据）。</div>
          ) : (
            alerts.map((a) => (
              <div
                key={a.id}
                className="flex items-center justify-between rounded-xl border border-zinc-200 bg-white px-4 py-3 text-sm dark:border-zinc-800 dark:bg-zinc-950"
              >
                <div className="min-w-0">
                  <div className="truncate">
                    <span
                      className={[
                        "mr-2 inline-block h-2 w-2 rounded-full",
                        a.severity === "red" ? "bg-rose-500" : "bg-amber-400",
                      ].join(" ")}
                    />
                    {a.dt} · {a.dimension} · {a.metric}
                  </div>
                </div>
                <div className="text-xs text-zinc-500">
                  {a.delta_pct == null ? "—" : `${(a.delta_pct * 100).toFixed(1)}%`}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
