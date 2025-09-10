import React, { useEffect, useState } from "react";
import axios from "axios";

const getApiBase = () => import.meta.env.VITE_API_URL || window.location.origin;

export default function SimulationEmbed() {
  const [files, setFiles] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const API = getApiBase();

  useEffect(() => {
    setLoading(true);
    axios
      .get(`${API}/simulation/vpython/list`)
      .then((res) => {
        setFiles(res.data.files || []);
        if ((res.data.files || []).length) setSelected(res.data.files[0]);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  function createPreset(preset = "solar", params = {}) {
    setCreating(true);
    axios
      .post(`${API}/simulation/vpython`, { preset, ...params })
      .then((res) => {
        const url = res.data.html_url;
        if (url) {
          // refresh list
          axios
            .get(`${API}/simulation/vpython/list`)
            .then((r) => {
              setFiles(r.data.files || []);
              const found = (r.data.files || []).find((f) =>
                url.endsWith(f.filename)
              );
              if (found) setSelected(found);
            })
            .catch(() => {});
        }
      })
      .catch(() => {})
      .finally(() => setCreating(false));
  }

  return (
    <div className="w-full lg:w-1/2">
      <div className="bg-white dark:bg-slate-800 rounded-lg shadow p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold">Live Simulation Preview</h3>
          <div className="flex gap-2">
            <button
              onClick={() => createPreset("solar")}
              disabled={creating}
              className="px-3 py-1 rounded bg-blue-600 text-white text-sm"
            >
              {creating ? "Creating..." : "Generate Solar"}
            </button>
            <button
              onClick={() =>
                createPreset("electric", { E_strength: 2.0, grid: 4 })
              }
              disabled={creating}
              className="px-3 py-1 rounded border text-sm"
            >
              Electric
            </button>
          </div>
        </div>

        {loading ? (
          <div>Loading sims...</div>
        ) : (
          <div className="grid grid-cols-1 gap-3">
            <select
              value={selected?.filename || ""}
              onChange={(e) =>
                setSelected(files.find((f) => f.filename === e.target.value))
              }
              className="p-2 rounded bg-slate-100 dark:bg-slate-700"
            >
              {files.map((f) => (
                <option key={f.filename} value={f.filename}>
                  {f.filename}
                </option>
              ))}
            </select>

            {selected ? (
              <div className="w-full h-64 border rounded overflow-hidden">
                <iframe
                  title="simulation-preview"
                  src={`${API}/simulation/vpython/preview/${selected.filename}`}
                  className="w-full h-full border-0"
                />
              </div>
            ) : (
              <div className="text-sm text-slate-500">
                No generated simulations yet — create one above.
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
