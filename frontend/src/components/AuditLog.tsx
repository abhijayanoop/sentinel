import type { AuditEntry } from "../types";

interface AuditLogProps {
  entries: AuditEntry[];
}

const ACTION_LABEL: Record<string, string> = {
  diagnosis_created: "Diagnosis created",
  approval_requested: "Approval requested",
  action_approved: "Action approved",
  action_rejected: "Action rejected",
  action_executed: "Action executed",
  execution_rejected: "Execution rejected",
  execution_failed: "Execution failed",
  verification_completed: "Verification completed",
};

const ACTOR_DOT: Record<string, string> = {
  agent: "bg-sky-400",
  system: "bg-slate-500",
};

function dotColor(actor: string): string {
  return ACTOR_DOT[actor] ?? "bg-accent";
}

function formatTime(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

export default function AuditLog({ entries }: AuditLogProps) {
  const ordered = [...entries].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
      <h3 className="text-sm font-semibold text-slate-300">Audit trail</h3>

      {ordered.length === 0 ? (
        <p className="mt-3 text-sm text-slate-500">No activity recorded yet.</p>
      ) : (
        <ol className="mt-4 flex flex-col">
          {ordered.map((entry, index) => (
            <li key={`${entry.created_at}-${index}`} className="relative pb-6 pl-6 last:pb-0">
              {index !== ordered.length - 1 && (
                <span className="absolute left-[3px] top-3 bottom-0 w-px bg-slate-800" />
              )}
              <span
                className={`absolute left-0 top-1.5 h-[7px] w-[7px] rounded-full ring-4 ring-slate-900/60 ${dotColor(entry.actor)}`}
              />
              <div className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1">
                <span className="text-sm font-medium text-slate-200">
                  {ACTION_LABEL[entry.action] ?? entry.action}
                </span>
                <span className="font-mono text-[11px] text-slate-500">{formatTime(entry.created_at)}</span>
              </div>
              <div className="mt-0.5 text-xs text-slate-500">
                by <span className="text-slate-400">{entry.actor}</span>
              </div>
              {entry.detail && Object.keys(entry.detail).length > 0 && (
                <pre className="mt-2 overflow-x-auto rounded-lg border border-slate-800 bg-slate-950/60 px-3 py-2 font-mono text-[11px] leading-relaxed text-slate-400">
                  {JSON.stringify(entry.detail, null, 2)}
                </pre>
              )}
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
