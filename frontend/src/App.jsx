import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./home.jsx"; // Your main page
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
