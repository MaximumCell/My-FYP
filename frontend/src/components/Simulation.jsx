import React from "react";
import SimulationEmbed from "./SimulationEmbed";
import { useNavigate } from "react-router-dom";

const Simulation = () => {
  const navigate = useNavigate();
  return (
    <section className="py-20 px-6">
      <div className="container mx-auto flex flex-col lg:flex-row items-start gap-8">
        <div className="w-full lg:w-1/2 space-y-6">
          <h2 className="text-3xl font-bold">
            Interactive Physics Simulations
          </h2>
          <p className="text-lg text-slate-600 dark:text-slate-300">
            Explore mechanics, electromagnetism, and planetary motion with
            interactive simulations you can modify and embed in reports or
            assignments.
          </p>
          <div className="flex gap-3">
            <button
              onClick={() => navigate("/simulation")}
              className="px-4 py-2 rounded bg-blue-600 text-white"
            >
              Open Simulation Box
            </button>
            <button
              onClick={() => navigate("/simulation")}
              className="px-4 py-2 rounded border"
            >
              Browse Presets
            </button>
          </div>
        </div>

        <SimulationEmbed />
      </div>
    </section>
  );
};

export default Simulation;
