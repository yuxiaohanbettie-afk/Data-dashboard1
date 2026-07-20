"use client";

import { useCallback, useMemo, useState } from "react";

type Props = {
  onFile: (file: File) => Promise<void>;
};

export function UploadDropzone({ onFile }: Props) {
  const [dragging, setDragging] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const border = useMemo(() => {
    if (dragging) return "border-emerald-500";
    return "border-zinc-200 dark:border-zinc-800";
  }, [dragging]);

  const handle = useCallback(
    async (file?: File | null) => {
      setError(null);
      if (!file) return;
      if (!file.name.toLowerCase().endsWith(".xlsx")) {
        setError("仅支持 .xlsx 文件");
        return;
      }
      await onFile(file);
    },
    [onFile],
  );

  return (
    <div>
      <label
        className={[
          "block rounded-xl border border-dashed bg-white p-8 text-center shadow-sm transition-colors dark:bg-zinc-950",
          border,
        ].join(" ")}
        onDragEnter={(e) => {
          e.preventDefault();
          e.stopPropagation();
          setDragging(true);
        }}
        onDragOver={(e) => {
          e.preventDefault();
          e.stopPropagation();
          setDragging(true);
        }}
        onDragLeave={(e) => {
          e.preventDefault();
          e.stopPropagation();
          setDragging(false);
        }}
        onDrop={(e) => {
          e.preventDefault();
          e.stopPropagation();
          setDragging(false);
          void handle(e.dataTransfer.files?.[0]);
        }}
      >
        <div className="text-sm font-medium">拖拽 Excel 到这里上传</div>
        <div className="mt-2 text-xs text-zinc-500">或点击选择文件</div>
        <input
          className="hidden"
          type="file"
          accept=".xlsx"
          onChange={(e) => void handle(e.target.files?.[0])}
        />
      </label>
      {error ? <div className="mt-3 text-sm text-rose-600">{error}</div> : null}
    </div>
  );
}

