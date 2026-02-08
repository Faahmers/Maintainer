import { useState, useRef, useEffect } from "react";

const API_BASE = "http://127.0.0.1:8000";

export default function MainContent() {
  const [repoUrl, setRepoUrl] = useState("");
  const [status, setStatus] = useState("Idle");
  const [prLink, setPrLink] = useState(null);
  const [logs, setLogs] = useState("");
  const [loading, setLoading] = useState(false);

  // 🔴 reference to log box for auto-scroll
  const logRef = useRef(null);

  // 🔴 auto-scroll when logs update
  useEffect(() => {
    if (logRef.current) {
      logRef.current.scrollTop = logRef.current.scrollHeight;
    }
  }, [logs]);

  const runMaintainer = async () => {
    if (!repoUrl) return;

    setLoading(true);
    setStatus("Starting AI maintainer...");
    setPrLink(null);
    setLogs("");

    try {
      // 1️⃣ POST /run
      const res = await fetch(`${API_BASE}/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ repo_url: repoUrl }),
      });

      const data = await res.json();
      const jobId = data.job_id;

      // 2️⃣ Poll /status
      const interval = setInterval(async () => {
        const sres = await fetch(`${API_BASE}/status/${jobId}`);
        const sdata = await sres.json();

        // 🔴 live logs while running
        if (sdata.logs) {
          setLogs(sdata.logs);
        }

        if (sdata.status === "running") {
          setStatus("AI is working...");
          return;
        }

        clearInterval(interval);
        setLoading(false);

        if (sdata.status === "error") {
          setStatus("❌ Error: " + sdata.error);
          return;
        }

        const result = sdata.result;

        setStatus("✅ " + result.message);
        setPrLink(result.pr_url);
        setLogs(result.logs || "");
      }, 2000);
    } catch (err) {
      setLoading(false);
      setStatus("❌ Network error");
    }
  };

  return (
    <main className="flex-grow flex items-center justify-center bg-gray-50 p-6">
      {/* 🔴 Wider card to match log console */}
      <div className="w-full max-w-4xl bg-white rounded-2xl shadow-xl border border-gray-100 p-8">

        {/* Title */}
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-gray-900">Deploy Project</h2>
          <p className="text-gray-500 text-sm mt-2">
            Enter a GitHub repo to run the AI maintainer
          </p>
        </div>

        {/* GitHub Input */}
        <div className="space-y-3">
          <label className="block text-sm font-semibold text-gray-700">
            Import from GitHub
          </label>

          <div className="flex gap-2">
            <input
              type="url"
              placeholder="github.com/username/repo"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              className="flex-1 px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 outline-none"
            />

            <button
              onClick={runMaintainer}
              disabled={loading}
              className="bg-gray-900 hover:bg-gray-800 text-white px-6 py-3 rounded-lg font-medium shadow-sm disabled:opacity-50"
            >
              {loading ? "Running..." : "Run"}
            </button>
          </div>
        </div>

        {/* Status */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">{status}</p>

          {prLink && (
            <a
              href={prLink}
              target="_blank"
              className="block mt-3 text-blue-600 font-semibold hover:underline"
            >
              Open Pull Request →
            </a>
          )}
        </div>

        {/* 🔴 Live Terminal-style Logs */}
        {logs && (
          <div className="mt-6">
            <p className="text-xs font-semibold text-gray-500 mb-2">
              Execution Logs
            </p>

            <pre
              ref={logRef}
              className="text-xs bg-gray-900 text-green-400 p-4 rounded-lg h-64 overflow-auto text-left whitespace-pre-wrap"
            >
              {logs}
            </pre>
          </div>
        )}

      </div>
    </main>
  );
}
