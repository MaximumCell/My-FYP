# PhysicsLab Architecture Diagram

Below is a simplified, screenshot‑friendly Mermaid diagram of the three-layer architecture. Open this file directly on GitHub for crisp rendering, then take your screenshot (you can also copy the Mermaid block into https://mermaid.live for SVG export).

> Tip: On GitHub, collapse the sidebar and use browser zoom 125% for higher resolution before taking a screenshot.

```mermaid
%% Three-Layer Architecture (Simplified)
flowchart LR
  %% Subgraphs (Layers)
  subgraph P[Presentation Layer]
    P1[Next.js / React / TS]
    P2[AI Chat (Gemini)]
    P3[Simulation UI]
    P4[ML Dashboard]
    P5[WebSocket + Upload]
  end

  subgraph A[Application Layer]
    A1[Flask API]
    A2[AI Tutor Service]
    A3[Simulation Engine]
    A4[ML Pipeline]
    A5[WebSocket Server]
    A6[Auth / Logging]
  end

  subgraph D[Data Layer]
    D1[MongoDB]
    D2[Qdrant]
    D3[Model Artifacts]
    D4[Plots & Assets]
    D5[Uploaded Files]
    D6[Secrets]
  end

  %% High-level flow
  User((User)) --> P
  P --> A --> D

  %% Specific mappings
  P2 --> A2
  P3 --> A3
  P4 <---> A4
  P5 <---> A5
  P1 --> A1

  A1 <---> D1
  A2 <---> D2
  A4 <---> D3
  A3 --> D4
  A1 <---> D5

  %% Secrets access (fan-in)
  A1 --> D6
  A2 --> D6
  A3 --> D6
  A4 --> D6
  A5 --> D6
  A6 --> D6
```

## Optional: Dark Theme Variant

If you prefer a dark screenshot, prepend the following directive before the diagram when using mermaid.live:

```
%%{init: { 'theme': 'dark', 'themeVariables': { 'fontFamily': 'Inter, Roboto, Arial', 'primaryColor': '#1e3a8a', 'primaryBorderColor': '#1e3a8a', 'lineColor': '#94a3b8', 'fontSize': '14px' } }}%%
```

Then paste the same diagram content below it.

---

Generated for quick, legible visualization.
