type Props = {
  title: string;
  value: string;
  diffPct?: number | null;
};

function pctText(v?: number | null) {
  if (v === null || v === undefined) return "—";
  const sign = v > 0 ? "+" : "";
  return `${sign}${(v * 100).toFixed(1)}%`;
}

export function KpiCard({ title, value, diffPct }: Props) {
  const up = diffPct !== null && diffPct !== undefined ? diffPct > 0 : null;
  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-4 shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
      <div className="text-xs text-zinc-500">{title}</div>
      <div className="mt-1 text-2xl font-semibold tracking-tight">{value}</div>
      <div
        className={[
          "mt-2 text-xs",
          up === null
            ? "text-zinc-500"
            : up
              ? "text-emerald-600"
              : "text-rose-600",
        ].join(" ")}
      >
        对比上一周期：{pctText(diffPct)}
      </div>
    </div>
  );
}

