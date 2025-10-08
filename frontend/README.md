# PhysicsLab Frontend

This is a Next.js application for PhysicsLab, a platform for machine learning model training, testing, and physics simulations.

## Getting Started

### Prerequisites

- Node.js (v18 or later)
- npm, yarn, or pnpm
- A running instance of the [PhysicsLab Flask backend](<your-backend-repo-link-here>).

### Environment Variables

Create a `.env.local` file in the root of the project and add the URL of your running backend:

```
NEXT_PUBLIC_API_URL=http://localhost:5000
```

If this variable is not set, the application will default to `http://localhost:5000`.

### Installation

Install the dependencies:

```bash
npm install
```

### Running the Development Server

To start the development server, run:

```bash
npm run dev
```

The application will be available at [http://localhost:9002](http://localhost:9002).

### Building for Production

To create a production build, run:

```bash
npm run build
```

And to start the production server:

```bash
npm run start
```

## Smoke Test

A simple smoke test script is provided to verify that the frontend can communicate with the backend. Make sure your backend server is running before executing the test.

The script will:
1.  Fetch the list of available regression models.
2.  Get the column names from the sample CSV file.
3.  Run a basic physics simulation.

To run the smoke test:

```bash
npm run test:smoke
```

You should see successful output for each step if the services are configured correctly.

## Manual Acceptance Testing

1.  **Navigate Home**: Open the app and ensure the home page loads correctly.
2.  **Navigate to ML Lab**: Click on "ML Lab". The page should load and fetch available models for the "Train" tab selects.
3.  **Get Columns**: In the "Train Models" tab, upload the `public/sample.csv` file. The "Target Column" select dropdown should populate with the column names from the file.
4.  **Recommend Model**: Go to the "Recommend Model" tab and upload `public/sample.csv`. The name of the recommended model should be displayed.
5.  **Run Simulation**: Navigate to the "Simulation" page. Click "Run Simulation" with default values. A plot image should appear. You should be able to download it.
