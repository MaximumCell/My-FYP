import { useState, useEffect } from "react";
import axios from "axios";

const TrainModel = () => {
  const [models, setModels] = useState([]);
  const [scalingMethods] = useState(["none", "standard", "minmax"]);
  const [selectedModel, setSelectedModel] = useState("");
  const [selectedScaler, setSelectedScaler] = useState("none");
  const [file, setFile] = useState(null);
  const [columns, setColumns] = useState([]); // State to store column names
  const [targetColumn, setTargetColumn] = useState(""); // State for selected target column
  const [downloadUrl, setDownloadUrl] = useState("");
  const [mse, setMSE] = useState(null);
  const [mae, setMAE] = useState(null);
  const [r2, setR2] = useState(null);
  const [testSize, setTestSize] = useState(0.2);
  const [hyperparams, setHyperparams] = useState("{}");
  const [error, setError] = useState("");
  // const [testData, setTestData] = useState(""); // Keep as string for now, will need parsing
  const [predictions, setPredictions] = useState([]);
  const [isTraining, setIsTraining] = useState(false);
  const [isTesting, setIsTesting] = useState(false);
  const [darkMode, setDarkMode] = useState(true);
  const [isDragOver, setIsDragOver] = useState(false);
  const [recommendedModel, setRecommendedModel] = useState("");

  // Fetch available models on component mount
  useEffect(() => {
    axios
      .get("http://127.0.0.1:5000/models/regression")
      .then((response) => setModels(response.data))
      .catch((error) => console.error("Error fetching models:", error));
  }, []);

  // Handle file upload and fetch column names
  const handleFileUpload = async (e) => {
    const uploadedFile = e.target.files[0];
    if (uploadedFile) {
      setFile(uploadedFile);
      setColumns([]); // Clear previous columns
      setTargetColumn(""); // Clear previous target selection
      setRecommendedModel(""); // Clear previous recommendation

      const formData = new FormData();
      formData.append("file", uploadedFile);

      try {
        // Fetch column names from the backend
        const columnsResponse = await axios.post(
          "http://127.0.0.1:5000/get_columns", // New backend endpoint
          formData
        );
        setColumns(columnsResponse.data.columns);

        // Fetch model recommendation (using the same file upload)
        // Corrected the typo in the URL here
        const recommendResponse = await axios.post(
          "http://127.0.0.1:5000/recommend",
          formData
        );
        setRecommendedModel(recommendResponse.data.recommended_model);
      } catch (error) {
        setError("Error processing file or getting columns/recommendation.");
        console.error("Error processing file:", error);
        setFile(null); // Clear file if error
      }
    }
  };

  const handleTrain = async () => {
    if (!file || !selectedModel || !targetColumn) {
      // Added targetColumn check
      setError(
        "Please select a model, upload a dataset, and select a target column."
      );
      return;
    }
    setError("");
    setIsTraining(true);
    setMSE(null); // Clear previous results
    setMAE(null);
    setR2(null);
    setDownloadUrl("");

    const formData = new FormData();
    formData.append("file", file);
    formData.append("model", selectedModel);
    formData.append(
      "scaling_method",
      selectedScaler === "none" ? "" : selectedScaler
    ); // Send empty string for 'none'
    formData.append("test_size", testSize);
    formData.append("hyperparams", hyperparams);
    formData.append("target_column", targetColumn); // Include selected target column

    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/train/regression",
        formData
      );
      // console.log("Response:", response.data);

      if (response.data.error) {
        setError(response.data.error);
      } else {
        const fullModelPath = response.data.model_path;
        // console.log("Model Path:", fullModelPath);

        // Find the last index of the backslash
        const lastBackslashIndex = fullModelPath.lastIndexOf('\\');

        let filenameWithExtension;
        if (lastBackslashIndex !== -1) {
          // Extract the filename including the extension
          filenameWithExtension = fullModelPath.substring(lastBackslashIndex + 1);
        } else {
          // If no backslash, assume the path is just the filename
          filenameWithExtension = fullModelPath;
        }

        const modelName = filenameWithExtension.replace('_pipeline.pkl', '');
        // console.log("Filename with Extension:", filenameWithExtension);
        // console.log("Model Name:", modelName);

        setDownloadUrl(modelName); // Set the base model name
        setMSE(response.data.mean_squared_error);
        setMAE(response.data.mean_absolute_error);
        setR2(response.data.r2_score);
      }
    } catch (error) {
      setError(
        error.response?.data?.error ||
          "Error training model. Please check your inputs."
      );
      console.error("Error training model:", error);
    }
    setIsTraining(false);
  };

  const [testData, setTestData] = useState({}); // State to store test feature values

  const handleTest = async () => {
    if (!selectedModel || Object.keys(testData).length === 0) {
      setError("Please select a model and enter test data.");
      return;
    }
    setError("");
    setIsTesting(true);

    try {
      const response = await axios.post(
        "http://127.0.0.1:5000/test/regression",
        {
          model: selectedModel,
          new_data: testData, // Send an object of feature: value
        }
      );

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
    <div
      className={`min-h-screen ${
        darkMode ? "bg-gray-900 text-white" : "bg-gray-100 text-gray-900"
      }`}
    >
      <div className="max-w-4xl mx-auto p-6">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold">
            Train & Test Your Model ("Classical Machine Learning Models")
          </h1>
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

        {/* File Upload Section */}
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
                handleFileUpload({ target: { files: [file] } }); // Use the existing handler
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
                {file && (
                  <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                    Selected file: {file.name}
                  </p>
                )}
                {recommendedModel && (
                  <p className="mt-2 text-green-600">
                    🔹 Recommended Model: <strong>{recommendedModel}</strong>
                  </p>
                )}
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
              onChange={handleFileUpload} // Use the updated handler
            />
          </div>
        </div>

        {/* Target Column Selection */}
        {columns.length > 0 && ( // Only show if columns are available
          <div className="mb-6">
            <label className="block text-lg font-medium mb-2">
              Select Target Column:
            </label>
            <select
              className={`w-full p-3 rounded-lg border ${
                darkMode
                  ? "bg-gray-800 border-gray-700"
                  : "bg-white border-gray-300"
              } focus:outline-none focus:ring-2 focus:ring-blue-500`}
              value={targetColumn}
              onChange={(e) => setTargetColumn(e.target.value)}
            >
              <option value="">-- Select Target Column --</option>
              {columns.map((col, index) => (
                <option key={index} value={col}>
                  {col}
                </option>
              ))}
            </select>
          </div>
        )}

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
            value={selectedModel} // Set value to show current selection
          >
            <option value="">-- Select Model --</option>
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
            value={selectedScaler} // Set value to show current selection
          >
            {/* Added 'none' option */}
            {scalingMethods.map((method, index) => (
              <option key={index} value={method}>
                {method.charAt(0).toUpperCase() + method.slice(1)}{" "}
                {/* Capitalize first letter */}
              </option>
            ))}
          </select>
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
            onChange={(e) => setTestSize(parseFloat(e.target.value))} // Parse to float
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
            value={hyperparams} // Set value to show current input
            onChange={(e) => setHyperparams(e.target.value)}
            rows="4" // Give it some height
          />
        </div>

        {/* Train Button */}
        <button
          onClick={handleTrain}
          disabled={isTraining || !file || !selectedModel || !targetColumn} // Disable if no file, model, or target
          className={`w-full py-3 rounded-lg font-semibold transition-colors ${
            isTraining || !file || !selectedModel || !targetColumn
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
            <div className="mt-4">
                <a
                    href={`http://127.0.0.1:5000/download/regression/${downloadUrl}`}
                    className="inline-block bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                    download={`trained_model_${selectedModel}.pkl`}
                >
                    Download Model
                </a>
            </div>
        )}
    </div>
)}

        {/* Test Section */}
        <h2 className="text-2xl font-bold mt-8 mb-6">Test Your Model</h2>
        {columns.length > 0 && targetColumn && (
          <div className="mb-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <h3 className="font-semibold mb-2 col-span-full">
              Enter Feature Values:
            </h3>
            {columns
              .filter((col) => col !== targetColumn)
              .map((col) => (
                <div key={col} className="mb-2">
                  <label
                    htmlFor={`test-${col}`}
                    className="block text-sm font-medium text-gray-700 capitalize"
                  >
                    {col.split("_").join(" ")}:
                  </label>
                  <input
                    type="number" // Or appropriate input type
                    id={`test-${col}`}
                    className={`w-full p-3 rounded-lg border ${
                      darkMode
                        ? "bg-gray-700 border-gray-600 text-gray-300" // Dark mode styling
                        : "bg-white border-gray-300 text-gray-700" // Light mode styling
                    } focus:outline-none focus:ring-2 focus:ring-blue-500 shadow-sm`} // Added shadow
                    onChange={(e) => {
                      setTestData((prevData) => ({
                        ...prevData,
                        [col]: parseFloat(e.target.value),
                      }));
                    }}
                  />
                </div>
              ))}
          </div>
        )}

        {/* Test Button */}
        <button
          onClick={handleTest}
          disabled={
            isTesting ||
            !targetColumn ||
            columns.filter((col) => col !== targetColumn).length === 0 ||
            Object.keys(testData).length !==
              columns.filter((col) => col !== targetColumn).length
          }
          className={`w-full py-3 mt-4 rounded-lg font-semibold transition-colors ${
            isTesting ||
            !targetColumn ||
            columns.filter((col) => col !== targetColumn).length === 0 ||
            Object.keys(testData).length !==
              columns.filter((col) => col !== targetColumn).length
              ? "bg-gray-500 cursor-not-allowed"
              : "bg-green-500 hover:bg-green-600 shadow-md" // Added shadow
          }`}
        >
          {isTesting ? "Testing..." : "Test Model"}
        </button>

        {/* Predictions */}
        {predictions.length > 0 && (
          <div className="mt-6 p-4 rounded-lg bg-blue-50 border border-blue-500 text-blue-700 shadow-sm">
            {" "}
            {/* Added shadow */}
            <h3 className="lg font-semibold mb-2">Predictions:</h3>
            {predictions.map((pred, index) => (
              <p key={index}>
                Prediction {index + 1}: {pred.toFixed(4)}
              </p>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default TrainModel;
