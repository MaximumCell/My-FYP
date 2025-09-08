import React, { useState, useEffect } from "react";
import axios from "axios";

const SimulationPage = () => {
  const [equation, setEquation] = useState("");
  const [xMin, setXMin] = useState(-10);
  const [xMax, setXMax] = useState(10);
  const [plotUrl, setPlotUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [selectedPredefined, setSelectedPredefined] = useState("");
  const [variableValues, setVariableValues] = useState({});
  const [errorMessage, setErrorMessage] = useState("");
  const [darkMode, setDarkMode] = useState(false);

  // Check user's preference for dark mode on initial load
  useEffect(() => {
    if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
      setDarkMode(true);
    }

    // Listen for changes in color scheme preference
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e) => setDarkMode(e.matches);
    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  // Updated equations to use 'x' consistently instead of 't'
  const predefinedEquations = {
    "Projectile Motion (y = v*x - 0.5*g*x^2)": ["v", "g"],
    "Simple Harmonic Motion (y = A*sin(w*x))": ["A", "w"],
    "Exponential Decay (y = A*e^(-k*x))": ["A", "k"],
    "Damped Oscillation (y = A*e^(-b*x) * cos(w*x))": ["A", "b", "w"],
    "Linear Motion (y = m*x + c)": ["m", "c"]
  };

  const handleVariableChange = (variable, value) => {
    setVariableValues({ ...variableValues, [variable]: parseFloat(value) });
  };

  const handleRunSimulation = async () => {
    if (!equation && !selectedPredefined) {
      alert("Please enter an equation or select a predefined one.");
      return;
    }

    setLoading(true);
    setPlotUrl(""); // Reset previous plot
    setErrorMessage(""); // Reset error message

    try {
      const response = await axios.post("http://127.0.0.1:5000/simulation", {
        equation: selectedPredefined || equation,
        x_min: xMin,
        x_max: xMax,
        variables: variableValues,
      });

      if (response.data.error) {
        setErrorMessage(response.data.error);
        setLoading(false);
        return;
      }

      // Add a small delay to simulate processing
      setTimeout(() => {
        if (response.data.plot_url) {
          // Use a timestamp to prevent browser caching
          setPlotUrl(`http://127.0.0.1:5000${response.data.plot_url}?t=${new Date().getTime()}`);
        }
        setLoading(false);
      }, 1000);
    } catch (error) {
      console.error("Error running simulation:", error);
      setErrorMessage("Server error: " + (error.response?.data?.error || error.message));
      setLoading(false);
    }
  };

  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  // Dynamic class names based on dark/light mode
  const containerClass = darkMode 
    ? "min-h-screen bg-gray-900 text-white flex flex-col items-center p-6 transition-colors duration-300" 
    : "min-h-screen bg-gray-50 text-gray-800 flex flex-col items-center p-6 transition-colors duration-300";
  
  const cardClass = darkMode
    ? "bg-gray-800 border border-gray-700 rounded-lg shadow-xl"
    : "bg-white border border-gray-200 rounded-lg shadow-lg";

  const inputClass = darkMode
    ? "bg-gray-700 border border-gray-600 text-white p-2 rounded-md w-full focus:ring-2 focus:ring-blue-500 focus:border-transparent"
    : "bg-white border border-gray-300 text-gray-800 p-2 rounded-md w-full focus:ring-2 focus:ring-blue-500 focus:border-transparent";

  const selectClass = darkMode
    ? "bg-gray-700 border border-gray-600 text-white p-2 rounded-md w-full focus:ring-2 focus:ring-blue-500 focus:border-transparent"
    : "bg-white border border-gray-300 text-gray-800 p-2 rounded-md w-full focus:ring-2 focus:ring-blue-500 focus:border-transparent";

  const buttonClass = "bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-2 rounded-md shadow transition duration-300 flex items-center justify-center";
  
  return (
    <div className={containerClass}>
      {/* Header with theme toggle */}
      <div className="w-full max-w-4xl flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Equation Simulation</h1>
        <button 
          onClick={toggleDarkMode} 
          className={`p-2 rounded-full ${darkMode ? 'bg-gray-700 text-yellow-300' : 'bg-gray-200 text-gray-800'}`}
        >
          {darkMode ? (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
            </svg>
          )}
        </button>
      </div>

      {/* Main content */}
      <div className={`${cardClass} w-full max-w-4xl p-6 mb-8`}>
        {/* Predefined Equation Selection */}
        <div className="mb-6">
          <label className="block font-medium mb-2">Select Predefined Equation:</label>
          <select
            className={selectClass}
            value={selectedPredefined}
            onChange={(e) => {
              setSelectedPredefined(e.target.value);
              setEquation(""); // Reset custom equation when selecting predefined
              setVariableValues({}); // Reset variables
              setErrorMessage(""); // Reset error messages
            }}
          >
            <option value="">Custom Equation</option>
            {Object.keys(predefinedEquations).map((eq) => (
              <option key={eq} value={eq}>
                {eq}
              </option>
            ))}
          </select>
        </div>

        {/* User Input for Variables (Only for Predefined Equations) */}
        {selectedPredefined && (
          <div className={`${darkMode ? 'bg-gray-700' : 'bg-gray-100'} p-4 rounded-lg mb-6`}>
            <h3 className="font-medium mb-3">Set Parameters:</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {predefinedEquations[selectedPredefined]?.map((variable) => (
                <div key={variable}>
                  <label className="block font-medium mb-1">{variable}:</label>
                  <input
                    type="number"
                    className={inputClass}
                    onChange={(e) => handleVariableChange(variable, e.target.value)}
                    placeholder={`Enter ${variable}`}
                  />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Custom Equation Input */}
        <div className="mb-6">
          <label className="block font-medium mb-2">
            {selectedPredefined ? "Or Enter Your Own Equation:" : "Enter Your Equation:"}
          </label>
          <input
            type="text"
            placeholder="e.g., x**2 + 2*x + 1"
            className={inputClass}
            value={equation}
            onChange={(e) => {
              setEquation(e.target.value);
              setErrorMessage("");
            }}
            disabled={selectedPredefined !== ""}
          />
        </div>

        {/* X Min & Max Inputs */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <label className="block font-medium mb-2">X Min:</label>
            <input
              type="number"
              className={inputClass}
              value={xMin}
              onChange={(e) => setXMin(parseFloat(e.target.value))}
            />
          </div>
          <div>
            <label className="block font-medium mb-2">X Max:</label>
            <input
              type="number"
              className={inputClass}
              value={xMax}
              onChange={(e) => setXMax(parseFloat(e.target.value))}
            />
          </div>
        </div>

        {/* Run Simulation Button */}
        <button
          className={buttonClass}
          onClick={handleRunSimulation}
          disabled={loading}
        >
          {loading ? (
            <>
              <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Running Simulation...
            </>
          ) : (
            "Run Simulation"
          )}
        </button>
      </div>

      {/* Display Error Message */}
      {errorMessage && (
        <div className={`${darkMode ? 'bg-red-900 border-red-800' : 'bg-red-100 border-red-200'} text-red-500 p-4 rounded-lg w-full max-w-4xl mb-6 border`}>
          <p className="font-bold">Error:</p>
          <p>{errorMessage}</p>
        </div>
      )}

      {/* Display Simulation Plot */}
      {plotUrl && !loading && (
        <div className={`${cardClass} w-full max-w-4xl overflow-hidden`}>
          <div className={`${darkMode ? 'bg-gray-700' : 'bg-gray-50'} px-6 py-4 border-b ${darkMode ? 'border-gray-600' : 'border-gray-200'}`}>
            <h2 className="text-lg font-bold">Simulation Result</h2>
          </div>
          <div className="p-6">
            <img
              src={plotUrl} 
              alt="Equation Plot"
              className="w-full rounded-lg border shadow-md"
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default SimulationPage;