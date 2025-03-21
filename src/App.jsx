import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Home from "./home.jsx"; // Your main page
import TrainModel from "./Pages/TrainModel.jsx"; // ML Training Page

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/train-ml" element={<TrainModel />} />
      </Routes>
    </Router>
  );
}

export default App;
