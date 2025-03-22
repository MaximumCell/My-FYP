import React, { useState, useEffect } from "react";
import axios from "axios";

const TrainModel = () => {
  const [models, setModels] = useState([]);
  const [scalingMethods] = useState(["none", "standard", "minmax"]);
  const [selectedModel, setSelectedModel] = useState("");
  const [selectedScaler, setSelectedScaler] = useState("none");
  const [file, setFile] = useState(null);
  const [downloadUrl, setDownloadUrl] = useState("");
  const [mse, setMSE] = useState(null);
  const [mae, setMAE] = useState(null);
  const [r2, setR2] = useState(null);
  const [targetColumn, setTargetColumn] = useState("");
  const [testSize, setTestSize] = useState(0.2);
  const [hyperparams, setHyperparams] = useState("{}");
  const [error, setError] = useState("");
  const [testData, setTestData] = useState("");
  const [predictions, setPredictions] = useState([]);
  const [isTraining, setIsTraining] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [darkMode, setDarkMode] = useState(true);
  const [isDragOver, setIsDragOver] = useState(false);
  const [recommendedModel, setRecommendedModel] = useState("");

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
    formData.append("scaling_method", selectedScaler);
    formData.append("test_size", testSize);
    formData.append("hyperparams", hyperparams);

    if (targetColumn.trim() !== "") {
      formData.append("target_column", targetColumn);
    }

    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/train",
        formData
      );

      setDownloadUrl(response.data.download_url);
      setMSE(response.data.mean_squared_error);
      setMAE(response.data.mean_absolute_error);
      setR2(response.data.r2_score);
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
      setError(
        "Invalid test data. Please enter only numbers separated by commas."
      );
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

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    setFile(file);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/recommend",
        formData
      );
      setRecommendedModel(response.data.recommended_model);
    } catch (error) {
      console.error("Error recommending model:", error);
    }
  };

  return (
    <div
      className={`min-h-screen ${
        darkMode ? "bg-gray-900 text-white" : "bg-gray-100 text-gray-900"
      }`}
    >
      <div className="max-w-4xl mx-auto p-6">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">Train & Test Your Model ("Classical Machine Learning Models")</h1>
          <button
            onClick={() => setDarkMode(!darkMode)}
            className={`px-4 py-2 rounded-lg transition-colors ${
              darkMode
                ? "bg-gray-700 hover:bg-gray-600"
                : "bg-gray-200 hover:bg-gray-300"
            }`}
          >
            {darkMode ? "☀️ Light Mode" : "🌙 Dark Mode"}
          </button>
        </div>

        {error && <p className="text-red-500 mb-6">{error}</p>}

        {/* Recommended Model */}
        <div className="mb-6">
          <label className="block text-lg font-medium mb-2">
            Upload Dataset (CSV):
          </label>
          <div className="flex flex-col items-center justify-center p-4 border-2 border-dashed border-gray-300 rounded-lg">
            <input
              type="file"
              className="hidden"
              id="file-upload"
              accept=".csv"
              onChange={handleFileUpload}
            />
            <label
              htmlFor="file-upload"
              className="text-blue-500 cursor-pointer hover:underline"
            >
              Click to upload a CSV file
            </label>
            <p className="text-sm text-gray-500 mt-2">
              or drag and drop your file here
            </p>
          </div>
          {recommendedModel && (
            <p className="mt-4 text-green-600">
              🔹 Recommended Model: <strong>{recommendedModel}</strong>
            </p>
          )}
        </div>
        {/* Model Selection */}
        <div className="mb-6">
          <label className="block text-lg font-medium mb-2">
            Select Model:
          </label>
          <select
            className={`w-full p-3 rounded-lg border ${
              darkMode
                ? "bg-gray-800 border-gray-700"
                : "bg-white border-gray-300"
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

        {/* Scaling Method */}
        <div className="mb-6">
          <label className="block text-lg font-medium mb-2">
            Scaling Method:
          </label>
          <select
            className={`w-full p-3 rounded-lg border ${
              darkMode
                ? "bg-gray-800 border-gray-700"
                : "bg-white border-gray-300"
            } focus:outline-none focus:ring-2 focus:ring-blue-500`}
            onChange={(e) => setSelectedScaler(e.target.value)}
          >
            {scalingMethods.map((method, index) => (
              <option key={index} value={method}>
                {method}
              </option>
            ))}
          </select>
        </div>

        {/* File Upload */}
        <div className="mb-6">
          <label className="block text-lg font-medium mb-2">
            Upload Dataset (CSV):
          </label>
          <div
            className={`w-full p-8 rounded-lg border-2 border-dashed ${
              darkMode
                ? "bg-gray-800 border-gray-700"
                : "bg-white border-gray-300"
            } flex flex-col items-center justify-center space-y-4 transition-colors ${
              isDragOver ? "border-blue-500 bg-blue-50" : ""
            } ${
              file ? "border-green-500 bg-green-50" : "" // Change styling after upload
            }`}
            onDragOver={(e) => {
              e.preventDefault();
              setIsDragOver(true);
            }}
            onDragLeave={() => setIsDragOver(false)}
            onDrop={(e) => {
              e.preventDefault();
              setIsDragOver(false);
              const file = e.dataTransfer.files[0];
              if (file && file.type === "text/csv") {
                setFile(file);
              }
            }}
          >
            {file ? ( // Show success state if file is uploaded
              <>
                <svg
                  className="w-12 h-12 text-green-500"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
                <p className="text-center text-green-600">
                  File uploaded successfully!
                </p>
              </>
            ) : (
              // Show default state if no file is uploaded
              <>
                <svg
                  className={`w-12 h-12 ${
                    darkMode ? "text-gray-400" : "text-gray-600"
                  }`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"
                  />
                </svg>
                <p
                  className={`text-center ${
                    darkMode ? "text-gray-400" : "text-gray-600"
                  }`}
                >
                  Drag & drop a CSV file here, or{" "}
                  <label
                    htmlFor="file-upload"
                    className="text-blue-500 cursor-pointer hover:underline"
                  >
                    browse your files
                  </label>
                </p>
              </>
            )}
            <input
              id="file-upload"
              type="file"
              className="hidden"
              accept=".csv"
              onChange={(e) => setFile(e.target.files[0])}
            />
          </div>
          {file && (
            <p className="mt-4 text-sm text-gray-600 dark:text-gray-400">
              Selected file: {file.name}
            </p>
          )}
        </div>

        {/* Test Size */}
        <div className="mb-6">
          <label className="block text-lg font-medium mb-2">
            Test Size (0.1 - 0.9):
          </label>
          <input
            type="number"
            step="0.1"
            min="0.1"
            max="0.9"
            value={testSize}
            className={`w-full p-3 rounded-lg border ${
              darkMode
                ? "bg-gray-800 border-gray-700"
                : "bg-white border-gray-300"
            } focus:outline-none focus:ring-2 focus:ring-blue-500`}
            onChange={(e) => setTestSize(e.target.value)}
          />
        </div>

        {/* Hyperparameters */}
        <div className="mb-6">
          <label className="block text-lg font-medium mb-2">
            Hyperparameters (JSON):
          </label>
          <textarea
            className={`w-full p-3 rounded-lg border ${
              darkMode
                ? "bg-gray-800 border-gray-700"
                : "bg-white border-gray-300"
            } focus:outline-none focus:ring-2 focus:ring-blue-500`}
            placeholder='{"n_estimators": 200}'
            onChange={(e) => setHyperparams(e.target.value)}
          />
        </div>

        {/* Train Button */}
        <button
          onClick={handleTrain}
          disabled={isTraining}
          className={`w-full py-3 rounded-lg font-semibold transition-colors ${
            isTraining
              ? "bg-gray-500 cursor-not-allowed"
              : "bg-blue-500 hover:bg-blue-600"
          }`}
        >
          {isTraining ? "Training..." : "Train Model"}
        </button>

        {/* Metrics */}
        {mse !== null && (
          <div className="mt-6 p-4 rounded-lg bg-green-50 border border-green-500">
            <p className="text-green-700">MSE: {mse.toFixed(4)}</p>
            <p className="text-green-700">R² Score: {r2.toFixed(4)}</p>
            <p className="text-green-700">MAE: {mae.toFixed(4)}</p>
            {downloadUrl && (
              <>
                <a
                  href={`http://127.0.0.1:5000${downloadUrl}`}
                  className="text-blue-500 hover:underline"
                  download
                >
                  Download Model
                </a>
              </>
            )}
          </div>
        )}

        {/* Test Section */}
        <h2 className="text-2xl font-bold mt-8 mb-6">Test Your Model</h2>
        <input
          type="text"
          placeholder="Enter comma-separated test data"
          className={`w-full p-3 rounded-lg border ${
            darkMode
              ? "bg-gray-800 border-gray-700"
              : "bg-white border-gray-300"
          } focus:outline-none focus:ring-2 focus:ring-blue-500`}
          onChange={(e) => setTestData(e.target.value)}
        />

        {/* Test Button */}
        <button
          onClick={handleTest}
          disabled={isTesting}
          className={`w-full py-3 mt-4 rounded-lg font-semibold transition-colors ${
            isTesting
              ? "bg-gray-500 cursor-not-allowed"
              : "bg-green-500 hover:bg-green-600"
          }`}
        >
          {isTesting ? "Testing..." : "Test Model"}
        </button>

        {/* Predictions */}
        {predictions.length > 0 && (
          <div className="mt-6 p-4 rounded-lg bg-blue-50 border border-blue-500">
            <h3 className="text-lg font-semibold mb-2">Predictions:</h3>
            {predictions.map((pred, index) => (
              <p key={index} className="text-blue-700">
                Prediction {index + 1}: {pred}
              </p>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default TrainModel;
