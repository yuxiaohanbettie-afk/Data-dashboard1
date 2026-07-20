export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000/api";

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(await res.text());
  return (await res.json()) as T;
}

export async function apiPostFile<T>(
  path: string,
  file: File,
  fieldName = "file",
): Promise<T> {
  const fd = new FormData();
  fd.append(fieldName, file);
  const res = await fetch(`${API_BASE}${path}`, { method: "POST", body: fd });
  if (!res.ok) throw new Error(await res.text());
  return (await res.json()) as T;
}

