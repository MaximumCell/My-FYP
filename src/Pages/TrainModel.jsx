import React, { useState, useEffect } from "react";
import axios from "axios";

const TrainModel = () => {
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState("");
  const [file, setFile] = useState(null);
  const [downloadUrl, setDownloadUrl] = useState("");
  const [mse, setMSE] = useState(null);
  const [targetColumn, setTargetColumn] = useState("");
  const [testSize, setTestSize] = useState(0.2);
  const [nEstimators, setNEstimators] = useState(10);
  const [maxIter, setMaxIter] = useState(1000);
  const [error, setError] = useState("");
  const [testData, setTestData] = useState("");
  const [predictions, setPredictions] = useState([]);
  const [samplePrediction, setSamplePrediction] = useState(null);
  const [isTraining, setIsTraining] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [darkMode, setDarkMode] = useState(true);

  useEffect(() => {
    axios
      .get("http://127.0.0.1:5000/models")
      .then((response) => setModels(response.data))
      .catch((error) => console.error("Error fetching models:", error));
  }, []);

  const handleTrain = async () => {
    if (!file || !selectedModel) {
      setError("Please select a model and upload a dataset.");
      return;
    }
    setError("");
    setIsTraining(true);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("model", selectedModel);

    if (targetColumn.trim() !== "") {
      formData.append("target_column", targetColumn);
    }

    formData.append("test_size", testSize);
    if (selectedModel === "random_forest") formData.append("n_estimators", nEstimators);
    if (selectedModel === "linear_regression") formData.append("max_iter", maxIter);

    try {
      const response = await axios.post("http://127.0.0.1:5000/train", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setDownloadUrl(response.data.download_url);
      setMSE(response.data.mean_squared_error);
      setSamplePrediction(response.data.sample_prediction);
    } catch (error) {
      setError("Error training model. Please check your inputs.");
      console.error("Error training model:", error);
    }
    setIsTraining(false);
  };

  const handleTest = async () => {
    if (!selectedModel || !testData) {
      setError("Please select a model and enter test data.");
      return;
    }
    setError("");
    setIsTesting(true);

    const inputData = testData
      .split(",")
      .map((num) => {
        const parsed = parseFloat(num.trim());
        return isNaN(parsed) ? null : parsed;
      })
      .filter((num) => num !== null);

    if (inputData.length === 0) {
      setError("Invalid test data. Please enter only numbers separated by commas.");
      setIsTesting(false);
      return;
    }

    try {
      const response = await axios.post("http://127.0.0.1:5000/test", {
        model: selectedModel,
        new_data: inputData,
      });

      if (response.data.predictions && response.data.predictions.length > 0) {
        setPredictions(response.data.predictions);
      }
    } catch (error) {
      setError(error.response?.data?.error || "Unknown error occurred.");
      console.error("Error testing model:", error);
    }
    setIsTesting(false);
  };

  return (
    <div className={`min-h-screen ${darkMode ? "bg-gray-900 text-white" : "bg-gray-100 text-gray-900"}`}>
      <div className="max-w-4xl mx-auto p-6">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Train & Test Your Model</h1>
          <button
            onClick={() => setDarkMode(!darkMode)}
            className={`px-4 py-2 rounded-lg ${
              darkMode ? "bg-gray-700 hover:bg-gray-600" : "bg-gray-200 hover:bg-gray-300"
            } transition-colors duration-300`}
          >
            {darkMode ? "☀️ Light Mode" : "🌙 Dark Mode"}
          </button>
        </div>

        {/* Error Message */}
        {error && <p className="text-red-500 mb-6">{error}</p>}

        {/* Model Selection */}
        <div className="mb-6">
          <label className="block text-lg font-medium mb-2">Select Model:</label>
          <select
            className={`w-full p-3 rounded-lg border ${
              darkMode ? "bg-gray-800 border-gray-700" : "bg-white border-gray-300"
            } focus:outline-none focus:ring-2 focus:ring-blue-500`}
            onChange={(e) => setSelectedModel(e.target.value)}
          >
            <option value="">Select Model</option>
            {models.map((model, index) => (
              <option key={index} value={model}>
                {model}
              </option>
            ))}
          </select>
        </div>

        {/* Target Column */}
        <div className="mb-6">
          <label className="block text-lg font-medium mb-2">Target Column (Optional):</label>
          <input
            type="text"
            placeholder="Leave blank to auto-select last column"
            className={`w-full p-3 rounded-lg border ${
              darkMode ? "bg-gray-800 border-gray-700" : "bg-white border-gray-300"
            } focus:outline-none focus:ring-2 focus:ring-blue-500`}
            onChange={(e) => setTargetColumn(e.target.value)}
          />
        </div>

        {/* File Upload */}
        <div className="mb-6">
          <label className="block text-lg font-medium mb-2">Upload Dataset (CSV):</label>
          <input
            type="file"
            className={`w-full p-3 rounded-lg border ${
              darkMode ? "bg-gray-800 border-gray-700" : "bg-white border-gray-300"
            } focus:outline-none focus:ring-2 focus:ring-blue-500`}
            accept=".csv"
            onChange={(e) => setFile(e.target.files[0])}
          />
        </div>

        {/* Train Button */}
        <button
          onClick={handleTrain}
          disabled={isTraining}
          className={`w-full py-3 rounded-lg font-semibold ${
            isTraining
              ? "bg-gray-500 cursor-not-allowed"
              : "bg-blue-500 hover:bg-blue-600"
          } text-white transition-colors duration-300`}
        >
          {isTraining ? "Training..." : "Train Model"}
        </button>

        {/* Training Results */}
        {mse !== null && (
          <div className="mt-6">
            <p className="text-lg">
              <strong>MSE:</strong> {mse.toFixed(4)}
            </p>
          </div>
        )}

        {samplePrediction && (
          <div className="mt-6">
            <p className="text-lg">
              <strong>Sample Prediction:</strong> Input: {samplePrediction.input.join(", ")} → Output:{" "}
              {samplePrediction.output}
            </p>
          </div>
        )}

        {downloadUrl && (
          <div className="mt-6">
            <a
              href={`http://127.0.0.1:5000${downloadUrl}`}
              className="text-green-500 hover:underline"
            >
              Download Trained Model
            </a>
          </div>
        )}

        {/* Test Section */}
        <h2 className="text-2xl font-bold mt-8 mb-6">Test Your Model</h2>
        <input
          type="text"
          placeholder="Enter comma-separated test data"
          className={`w-full p-3 rounded-lg border ${
            darkMode ? "bg-gray-800 border-gray-700" : "bg-white border-gray-300"
          } focus:outline-none focus:ring-2 focus:ring-blue-500`}
          onChange={(e) => setTestData(e.target.value)}
        />

        {/* Test Button */}
        <button
          onClick={handleTest}
          disabled={isTesting}
          className={`w-full py-3 mt-4 rounded-lg font-semibold ${
            isTesting
              ? "bg-gray-500 cursor-not-allowed"
              : "bg-green-500 hover:bg-green-600"
          } text-white transition-colors duration-300`}
        >
          {isTesting ? "Testing..." : "Test Model"}
        </button>

        {/* Test Results */}
        {predictions.length > 0 && (
          <div className="mt-6">
            <h3 className="text-lg font-bold mb-2">Prediction Results:</h3>
            <div className="space-y-2">
              {predictions.map((pred, index) => (
                <p key={index} className="text-lg">
                  Prediction {index + 1}: {pred}
                </p>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TrainModel;