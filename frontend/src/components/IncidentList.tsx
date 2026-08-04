import type { Incident, IncidentStatus } from "../types";

interface IncidentListProps {
  incidents: Incident[];
  selectedId: number | null;
  onSelect: (id: number) => void;
  loading: boolean;
  error: string | null;
}

const STATUS_STYLES: Record<IncidentStatus, string> = {
  pending: "bg-amber-400/10 text-amber-300 ring-1 ring-inset ring-amber-400/30",
  diagnosed: "bg-sky-400/10 text-sky-300 ring-1 ring-inset ring-sky-400/30",
  resolved: "bg-emerald-400/10 text-emerald-300 ring-1 ring-inset ring-emerald-400/30",
  action_failed: "bg-rose-400/10 text-rose-300 ring-1 ring-inset ring-rose-400/30",
};

const STATUS_DOT: Record<IncidentStatus, string> = {
  pending: "bg-amber-400",
  diagnosed: "bg-sky-400",
  resolved: "bg-emerald-400",
  action_failed: "bg-rose-400",
};

const STATUS_LABEL: Record<IncidentStatus, string> = {
  pending: "Pending",
  diagnosed: "Diagnosed",
  resolved: "Resolved",
  action_failed: "Action failed",
};

export function StatusBadge({ status }: { status: IncidentStatus }) {
  const isLive = status === "pending" || status === "diagnosed";
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-[11px] font-medium tracking-wide whitespace-nowrap ${STATUS_STYLES[status]}`}
    >
      <span className="relative flex h-1.5 w-1.5">
        {isLive && (
          <span
            className={`absolute inline-flex h-full w-full animate-pulse-ring rounded-full ${STATUS_DOT[status]}`}
          />
        )}
        <span className={`relative inline-flex h-1.5 w-1.5 rounded-full ${STATUS_DOT[status]}`} />
      </span>
      {STATUS_LABEL[status]}
    </span>
  );
}

function formatTime(iso: string): string {
  const date = new Date(iso);
  return date.toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default function IncidentList({ incidents, selectedId, onSelect, loading, error }: IncidentListProps) {
  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between border-b border-slate-800/80 px-4 py-3.5">
        <h2 className="text-sm font-semibold tracking-wide text-slate-200">Incidents</h2>
        <span className="rounded-md bg-slate-800/70 px-2 py-0.5 font-mono text-[11px] text-slate-400">
          {incidents.length}
        </span>
      </div>

      <div className="flex-1 overflow-y-auto">
        {error && (
          <div className="m-3 rounded-lg border border-rose-500/20 bg-rose-500/5 px-3 py-2 text-xs text-rose-300">
            {error}
          </div>
        )}

        {loading && incidents.length === 0 && (
          <div className="flex flex-col gap-2 p-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-16 animate-pulse rounded-xl bg-slate-800/40" />
            ))}
          </div>
        )}

        {!loading && incidents.length === 0 && !error && (
          <div className="px-4 py-10 text-center text-sm text-slate-500">
            No incidents yet. Sentinel is watching.
          </div>
        )}

        <ul className="flex flex-col gap-1 p-2">
          {incidents.map((incident) => {
            const active = incident.id === selectedId;
            return (
              <li key={incident.id}>
                <button
                  type="button"
                  onClick={() => onSelect(incident.id)}
                  className={`group relative w-full rounded-xl px-3 py-3 text-left transition-all duration-150 ${
                    active
                      ? "bg-slate-800/80 shadow-glow ring-1 ring-sky-500/30"
                      : "hover:bg-slate-800/40"
                  }`}
                >
                  {active && (
                    <span className="absolute left-0 top-3 bottom-3 w-0.5 rounded-full bg-accent" />
                  )}
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-mono text-xs text-slate-400">
                      #{String(incident.id).padStart(4, "0")}
                    </span>
                    <StatusBadge status={incident.status} />
                  </div>
                  <div className="mt-1.5 flex items-center justify-between gap-2">
                    <span className="truncate text-sm font-medium text-slate-200">
                      {incident.source}
                    </span>
                    <span className="shrink-0 text-[11px] text-slate-500">
                      {formatTime(incident.created_at)}
                    </span>
                  </div>
                </button>
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
}
