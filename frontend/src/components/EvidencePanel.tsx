import { useState } from "react";
import type { Diagnosis } from "../types";

interface EvidencePanelProps {
  diagnosis: Diagnosis | null;
}

export default function EvidencePanel({ diagnosis }: EvidencePanelProps) {
  const refs = diagnosis?.evidence_refs?.evidence ?? [];
  const [openTools, setOpenTools] = useState<Set<number>>(new Set([0]));

  const toggle = (index: number) => {
    setOpenTools((prev) => {
      const next = new Set(prev);
      if (next.has(index)) {
        next.delete(index);
      } else {
        next.add(index);
      }
      return next;
    });
  };

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-5">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-300">Evidence</h3>
        <span className="rounded-md bg-slate-800/70 px-2 py-0.5 font-mono text-[11px] text-slate-400">
          {refs.length}
        </span>
      </div>

      {refs.length === 0 ? (
        <p className="mt-3 text-sm text-slate-500">No evidence collected yet.</p>
      ) : (
        <ul className="mt-3 flex flex-col gap-2">
          {refs.map((ref, index) => {
            const open = openTools.has(index);
            return (
              <li
                key={`${ref.tool_name}-${index}`}
                className="overflow-hidden rounded-xl border border-slate-800 bg-slate-950/40"
              >
                <button
                  type="button"
                  onClick={() => toggle(index)}
                  className="flex w-full items-center justify-between gap-3 px-4 py-3 text-left transition-colors hover:bg-slate-800/30"
                >
                  <span className="flex items-center gap-2 min-w-0">
                    <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-accent" />
                    <span className="truncate font-mono text-xs text-slate-300">{ref.tool_name}</span>
                  </span>
                  <svg
                    className={`h-4 w-4 shrink-0 text-slate-500 transition-transform duration-200 ${open ? "rotate-180" : ""}`}
                    viewBox="0 0 20 20"
                    fill="currentColor"
                  >
                    <path
                      fillRule="evenodd"
                      d="M5.23 7.21a.75.75 0 011.06.02L10 11.168l3.71-3.938a.75.75 0 111.08 1.04l-4.25 4.5a.75.75 0 01-1.08 0l-4.25-4.5a.75.75 0 01.02-1.06z"
                      clipRule="evenodd"
                    />
                  </svg>
                </button>
                {open && (
                  <div className="animate-fade-in border-t border-slate-800/80 px-4 py-3 text-sm leading-relaxed text-slate-300">
                    {ref.summary}
                  </div>
                )}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
