import { useCallback, useEffect, useRef, useState } from "react";
import { getIncidents, getIncident, ApiError, clearToken } from "../api/client";
import type { Incident, IncidentDetail } from "../types";
import IncidentList, { StatusBadge } from "../components/IncidentList";
import DiagnosisCard from "../components/DiagnosisCard";
import EvidencePanel from "../components/EvidencePanel";
import ApprovalActions from "../components/ApprovalActions";
import AuditLog from "../components/AuditLog";

const POLL_INTERVAL_MS = 5000;

interface DashboardPageProps {
  onLogout: () => void;
}

function formatFullTime(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "medium",
  });
}

export default function DashboardPage({ onLogout }: DashboardPageProps) {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [listLoading, setListLoading] = useState(true);
  const [listError, setListError] = useState<string | null>(null);

  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [detail, setDetail] = useState<IncidentDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);

  const selectedIdRef = useRef<number | null>(null);
  selectedIdRef.current = selectedId;

  const handleAuthFailure = useCallback(() => {
    clearToken();
    onLogout();
  }, [onLogout]);

  const fetchIncidents = useCallback(
    async (isInitial: boolean) => {
      if (isInitial) setListLoading(true);
      try {
        const data = await getIncidents();
        setIncidents(data);
        setListError(null);
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) {
          handleAuthFailure();
          return;
        }
        setListError(err instanceof ApiError ? err.message : "Failed to load incidents.");
      } finally {
        if (isInitial) setListLoading(false);
      }
    },
    [handleAuthFailure]
  );

  const fetchDetail = useCallback(
    async (id: number, isInitial: boolean) => {
      if (isInitial) setDetailLoading(true);
      try {
        const data = await getIncident(id);
        if (selectedIdRef.current === id) {
          setDetail(data);
          setDetailError(null);
        }
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) {
          handleAuthFailure();
          return;
        }
        if (selectedIdRef.current === id) {
          setDetailError(err instanceof ApiError ? err.message : "Failed to load incident detail.");
        }
      } finally {
        if (isInitial && selectedIdRef.current === id) setDetailLoading(false);
      }
    },
    [handleAuthFailure]
  );

  useEffect(() => {
    fetchIncidents(true);
    const interval = setInterval(() => fetchIncidents(false), POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [fetchIncidents]);

  useEffect(() => {
    if (selectedId === null) {
      setDetail(null);
      return;
    }
    fetchDetail(selectedId, true);
    const interval = setInterval(() => fetchDetail(selectedId, false), POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [selectedId, fetchDetail]);

  const handleResolved = useCallback(async () => {
    if (selectedId !== null) {
      await fetchDetail(selectedId, false);
    }
    await fetchIncidents(false);
  }, [selectedId, fetchDetail, fetchIncidents]);

  return (
    <div className="flex h-screen flex-col bg-slate-950">
      <header className="flex items-center justify-between border-b border-slate-800/80 bg-slate-950/80 px-5 py-3 backdrop-blur-sm">
        <div className="flex items-center gap-2.5">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-sky-400 to-indigo-500">
            <svg viewBox="0 0 24 24" fill="none" className="h-4 w-4 text-slate-950">
              <path
                d="M12 2 4 5.5v6c0 5.25 3.4 9.9 8 11 4.6-1.1 8-5.75 8-11v-6L12 2Z"
                fill="currentColor"
              />
            </svg>
          </div>
          <span className="text-sm font-semibold tracking-wide text-slate-200">Sentinel</span>
          <span className="ml-1 rounded-md bg-slate-800/70 px-2 py-0.5 text-[11px] font-medium text-slate-400">
            Live
          </span>
        </div>
        <button
          type="button"
          onClick={onLogout}
          className="rounded-lg px-3 py-1.5 text-xs font-medium text-slate-400 transition-colors hover:bg-slate-800/60 hover:text-slate-200"
        >
          Sign out
        </button>
      </header>

      <div className="flex min-h-0 flex-1">
        <aside className="w-[340px] shrink-0 border-r border-slate-800/80 bg-slate-950/40">
          <IncidentList
            incidents={incidents}
            selectedId={selectedId}
            onSelect={setSelectedId}
            loading={listLoading}
            error={listError}
          />
        </aside>

        <main className="flex-1 overflow-y-auto bg-noise">
          {selectedId === null && (
            <div className="flex h-full flex-col items-center justify-center gap-2 text-center">
              <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-slate-800 bg-slate-900/60">
                <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5 text-slate-600">
                  <path
                    d="M9 12l2 2 4-4m5-2a9 9 0 11-18 0 9 9 0 0118 0z"
                    stroke="currentColor"
                    strokeWidth="1.5"
                  />
                </svg>
              </div>
              <p className="text-sm text-slate-500">Select an incident to view details</p>
            </div>
          )}

          {selectedId !== null && detailLoading && !detail && (
            <div className="flex flex-col gap-4 p-6">
              <div className="h-24 animate-pulse rounded-2xl bg-slate-800/40" />
              <div className="h-40 animate-pulse rounded-2xl bg-slate-800/40" />
              <div className="h-32 animate-pulse rounded-2xl bg-slate-800/40" />
            </div>
          )}

          {selectedId !== null && detailError && !detail && (
            <div className="p-6">
              <div className="rounded-xl border border-rose-500/20 bg-rose-500/5 px-4 py-3 text-sm text-rose-300">
                {detailError}
              </div>
            </div>
          )}

          {detail && (
            <div className="mx-auto flex max-w-3xl flex-col gap-5 p-6 animate-fade-in">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <div className="flex items-center gap-2.5">
                    <h1 className="font-mono text-lg font-semibold text-slate-100">
                      Incident #{String(detail.id).padStart(4, "0")}
                    </h1>
                    <StatusBadge status={detail.status} />
                  </div>
                  <p className="mt-1 text-sm text-slate-500">
                    Source: <span className="text-slate-400">{detail.source}</span> · Reported{" "}
                    {formatFullTime(detail.created_at)}
                  </p>
                </div>
              </div>

              <ApprovalActions
                incidentId={detail.id}
                approval={detail.approval}
                onResolved={handleResolved}
              />

              <DiagnosisCard diagnosis={detail.diagnosis} />

              <EvidencePanel diagnosis={detail.diagnosis} />

              <AuditLog entries={detail.audit_log} />
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
