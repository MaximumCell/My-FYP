/**
 * Main App Component
 * 
 * This component sets up the main routing structure for the Physics Simulation & ML Project.
 * It includes routes for:
 * - Home page with project overview
 * - ML model training interface
 * - Physics simulation visualization
 * - ML model testing and classification
 * 
 * @returns {JSX.Element} The main application component
 */

import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import {Home} from "./home.jsx"; // Your main page
import TrainModel from "./Pages/TrainModel.jsx"; // ML Training Page
import SimulationPage from "./Pages/SimulationPage.jsx";
import MLPage from "./Pages/MLPage.jsx";
import ClassificationModelPage from "./Pages/ClassificationModelPage.jsx";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/ml" element={<MLPage />} />
        <Route path="/regression" element={<TrainModel />} />
        <Route path="/classification" element={<ClassificationModelPage />} />
        <Route path="/simulation" element={<SimulationPage />} />
      </Routes>
    </Router>
  );
}

export default App;
