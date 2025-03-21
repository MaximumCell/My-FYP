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

  useEffect(() => {
    axios
      .get("http://127.0.0.1:5000/models")
      .then((response) => setModels(response.data))
      .catch((error) => console.error("Error fetching models:", error));
  }, []);

  const handleTrain = async () => {
    if (!file || !selectedModel || !targetColumn) {
      setError("Please select a model, target column, and upload a dataset.");
      return;
    }
    setError("");
    setIsTraining(true);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("model", selectedModel);
    formData.append("target_column", targetColumn);
    formData.append("test_size", testSize);
    if (selectedModel === "random_forest")
      formData.append("n_estimators", nEstimators);
    if (selectedModel === "linear_regression")
      formData.append("max_iter", maxIter);

    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/train",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );

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
  
    const inputData = testData.split(",").map((num) => {
      const parsed = parseFloat(num.trim());
      return isNaN(parsed) ? null : parsed;
    }).filter(num => num !== null);
  
    if (inputData.length === 0) {
      setError("Invalid test data. Please enter only numbers separated by commas.");
      setIsTesting(false);
      return;
    }
  
    try {
      console.log("🚀 Sending request to backend...");
      const response = await axios.post("http://127.0.0.1:5000/test", {
        model: selectedModel,
        new_data: inputData
      });
  
      console.log("✅ Response received:", response.data);
      
      // ✅ Check if predictions exist before setting state
      if (response.data.predictions && response.data.predictions.length > 0) {
        console.log("🎯 Predictions:", response.data.predictions);
        setPredictions(response.data.predictions);
      } else {
        console.warn("⚠️ No predictions received");
      }
  
    } catch (error) {
      console.error("❌ Error testing model:", error.response?.data || error);
      setError(error.response?.data?.error || "Unknown error occurred.");
    }
    setIsTesting(false);
  };
  
  return (
    <div className="p-6">
      <h2 className="text-xl font-bold">Train & Preview Your Model</h2>

      {error && <p className="text-red-500">{error}</p>}

      <div className="mt-4">
        <label className="block text-gray-700">Select Model:</label>
        <select
          className="border p-2 w-full"
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

      <div className="mt-4">
        <label className="block text-gray-700">Target Column:</label>
        <input
          type="text"
          placeholder="Enter target column"
          className="border p-2 w-full"
          onChange={(e) => setTargetColumn(e.target.value)}
        />
      </div>

      <div className="mt-4">
        <label className="block text-gray-700">Upload Dataset (CSV):</label>
        <input
          type="file"
          className="border p-2 w-full"
          accept=".csv"
          onChange={(e) => setFile(e.target.files[0])}
        />
      </div>

      <div className="mt-4">
        <label className="block text-gray-700">Test Size (0.1 - 0.9):</label>
        <input
          type="number"
          step="0.1"
          min="0.1"
          max="0.9"
          value={testSize}
          className="border p-2 w-full"
          onChange={(e) => setTestSize(e.target.value)}
        />
      </div>

      {selectedModel === "random_forest" && (
        <div className="mt-4">
          <label className="block text-gray-700">
            n_estimators (RandomForest):
          </label>
          <input
            type="number"
            value={nEstimators}
            className="border p-2 w-full"
            onChange={(e) => setNEstimators(e.target.value)}
          />
        </div>
      )}

      {selectedModel === "linear_regression" && (
        <div className="mt-4">
          <label className="block text-gray-700">
            max_iter (Linear Regression):
          </label>
          <input
            type="number"
            value={maxIter}
            className="border p-2 w-full"
            onChange={(e) => setMaxIter(e.target.value)}
          />
        </div>
      )}

      <button
        onClick={handleTrain}
        disabled={isTraining}
        className={`mt-4 bg-blue-500 ${
          isTraining ? "opacity-50" : "hover:bg-blue-600"
        } text-white font-semibold py-2 px-6 rounded-lg transition-all duration-300`}
      >
        {isTraining ? "Training..." : "Train Model"}
      </button>

      {mse !== null && (
        <p className="mt-4 text-lg text-gray-700">
          <strong>MSE:</strong> {mse.toFixed(4)}
        </p>
      )}

      {samplePrediction !== null && (
        <p className="mt-4 text-lg text-gray-700">
          <strong>Sample Prediction:</strong> Input:{" "}
          {samplePrediction.input.join(", ")} → Output:{" "}
          {samplePrediction.output}
        </p>
      )}

      {downloadUrl && (
        <div className="mt-4">
          <a
            href={`http://127.0.0.1:5000${downloadUrl}`}
            className="text-green-600 font-semibold"
          >
            Download Trained Model
          </a>
        </div>
      )}

      <h2 className="text-xl font-bold mt-6">Test Your Model</h2>
      <input
        type="text"
        placeholder="Enter comma-separated test data"
        className="border p-2 mt-2 w-full"
        onChange={(e) => setTestData(e.target.value)}
      />
      <button
        onClick={handleTest}
        disabled={isTesting}
        className={`mt-2 bg-green-500 ${
          isTesting ? "opacity-50" : "hover:bg-green-600"
        } text-white font-semibold py-2 px-6 rounded-lg transition-all duration-300`}
      >
        {isTesting ? "Testing..." : "Test Model"}
      </button>

      {predictions.length > 0 && (
        <div className="mt-4">
          <h3 className="text-lg font-bold">Prediction Results:</h3>
          <p className="text-gray-700">
            {predictions.map((pred, index) => (
              <span key={index} className="block">{`Prediction ${
                index + 1
              }: ${pred}`}</span>
            ))}
          </p>
        </div>
      )}
    </div>
  );
};

export default TrainModel;
