"use client";

import { useState } from "react";
import { UploadDropzone } from "@/components/UploadDropzone";
import { apiPostFile } from "@/lib/api";

type UploadImportResponse = {
  upload_id: number;
  rows_total: number;
  rows_imported: number;
  rows_skipped: number;
  db_total_rows: number;
  latest_upload_time: string;
};

export default function UploadPage() {
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<UploadImportResponse | null>(null);
  const [err, setErr] = useState<string | null>(null);

  async function onFile(file: File) {
    setBusy(true);
    setErr(null);
    setResult(null);
    try {
      const res = await apiPostFile<UploadImportResponse>("/upload/excel", file);
      setResult(res);
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="p-6 md:p-8">
      <div className="flex items-center justify-between gap-4">
        <div>
          <div className="text-sm text-zinc-500">Upload Center</div>
          <h1 className="mt-1 text-2xl font-semibold tracking-tight">导入 Excel</h1>
        </div>
        <a
          className="h-10 inline-flex items-center rounded-lg border border-zinc-200 bg-white px-3 text-sm hover:bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-950 dark:hover:bg-zinc-900"
          href="/"
        >
          返回首页
        </a>
      </div>

      <div className="mt-6">
        <UploadDropzone onFile={onFile} />
        <div className="mt-3 text-xs text-zinc-500">
          导入流程：Upload → Validate → Parse → Transform → Append SQLite → Refresh Dashboard → Detect
          Anomalies
        </div>
      </div>

      {busy ? (
        <div className="mt-6 rounded-xl border border-zinc-200 bg-white p-4 text-sm dark:border-zinc-800 dark:bg-zinc-950">
          正在导入…（首次导入会更慢）
        </div>
      ) : null}

      {err ? (
        <div className="mt-6 rounded-xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700 dark:border-rose-900/50 dark:bg-rose-950/30 dark:text-rose-200">
          导入失败：{err}
        </div>
      ) : null}

      {result ? (
        <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-950">
            <div className="text-xs text-zinc-500">Rows Imported</div>
            <div className="mt-1 text-2xl font-semibold">{result.rows_imported}</div>
          </div>
          <div className="rounded-xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-950">
            <div className="text-xs text-zinc-500">Rows Skipped</div>
            <div className="mt-1 text-2xl font-semibold">{result.rows_skipped}</div>
          </div>
          <div className="rounded-xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-950">
            <div className="text-xs text-zinc-500">Database Total Rows</div>
            <div className="mt-1 text-2xl font-semibold">{result.db_total_rows}</div>
          </div>
          <div className="rounded-xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-950">
            <div className="text-xs text-zinc-500">Latest Upload Time</div>
            <div className="mt-1 text-sm font-medium">{result.latest_upload_time}</div>
          </div>
        </div>
      ) : null}

      <div className="mt-10 rounded-xl border border-zinc-200 bg-white p-4 text-sm text-zinc-600 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-300">
        <div className="font-medium text-zinc-900 dark:text-zinc-100">去重逻辑</div>
        <div className="mt-2">
          系统会对每一行计算 `row_hash`（基于原始 Excel 字段），并在 SQLite 上做唯一约束；同一份数据重复导入会自动
          `skip`，历史数据不会被覆盖或删除。
        </div>
      </div>
    </div>
  );
}

