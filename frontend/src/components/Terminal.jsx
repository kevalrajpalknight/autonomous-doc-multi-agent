import { TerminalIcon, X } from "lucide-react";
import { useEffect, useRef } from "react";

export function Terminal({ logs, onClose, isVisible }) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [logs]);

  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl max-h-[90vh] bg-slate-950 rounded-2xl border border-white/10 shadow-2xl flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-white/10">
          <div className="flex items-center gap-2">
            <TerminalIcon size={20} className="text-green-400" />
            <span className="font-mono text-white font-semibold">
              Processing...
            </span>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-white/10 rounded-lg transition-colors"
          >
            <X size={20} className="text-white" />
          </button>
        </div>

        {/* Terminal Content */}
        <div className="flex-1 overflow-y-auto bg-black/40 p-4 font-mono text-sm">
          {logs.map((log, idx) => (
            <div key={idx} className="text-green-400 mb-1 leading-relaxed">
              <span className="text-gray-500">{">"}</span> {log}
            </div>
          ))}
          <div ref={endRef} />
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-white/10 bg-slate-900/50 text-xs text-gray-400 flex items-center gap-2">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
          Processing {logs.length} log entries
        </div>
      </div>
    </div>
  );
}
