import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ClassificationModelPage = () => {
  const [models, setModels] = useState([]);
  const [file, setFile] = useState(null);
  const [columns, setColumns] = useState([]);
  const [targetColumn, setTargetColumn] = useState('');
  const [selectedModel, setSelectedModel] = useState('');
  const [hyperparams, setHyperparams] = useState('{}');
  const [accuracy, setAccuracy] = useState(null);
  const [precision, setPrecision] = useState(null);
  const [recall, setRecall] = useState(null);
  const [f1Score, setF1Score] = useState(null);
  const [confusionMatrix, setConfusionMatrix] = useState(null);
  const [rocAuc, setRocAuc] = useState(null);
  const [classNames, setClassNames] = useState([]);
  const [downloadUrl, setDownloadUrl] = useState('');
  const [error, setError] = useState('');
  const [isTraining, setIsTraining] = useState(false);
  const [darkMode, setDarkMode] = useState(true);
  const [isDragOver, setIsDragOver] = useState(false);
  const [recommendedModel, setRecommendedModel] = useState('');

  useEffect(() => {
    axios.get('http://127.0.0.1:5000/models/classification')
      .then(response => setModels(response.data))
      .catch(error => console.error('Error fetching classification models:', error));
  }, []);

  const handleFileUpload = async (e) => {
    const uploadedFile = e.target.files[0];
    if (uploadedFile) {
      setFile(uploadedFile);
      setColumns([]);
      setTargetColumn('');
      setRecommendedModel('');
      const formData = new FormData();
      formData.append('file', uploadedFile);
      try {
        const columnsResponse = await axios.post('http://127.0.0.1:5000/get_columns', formData);
        setColumns(columnsResponse.data.columns);
        const recommendResponse = await axios.post('http://127.0.0.1:5000/models/classification', formData);
        setRecommendedModel(recommendResponse.data.recommended_model);
      } catch (error) {
        setError('Error processing file or getting columns/recommendation.');
        console.error('Error processing file:', error);
        setFile(null);
      }
    }
  };

  const handleTrain = async () => {
    if (!file || !selectedModel || !targetColumn) {
      setError('Please select a file, model, and target column.');
      return;
    }
    setError('');
    setIsTraining(true);
    setAccuracy(null);
    setPrecision(null);
    setRecall(null);
    setF1Score(null);
    setConfusionMatrix(null);
    setRocAuc(null);
    setDownloadUrl('');
    setClassNames([]);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('model', selectedModel);
    formData.append('target_column', targetColumn);
    formData.append('hyperparams', hyperparams);

    try {
      const response = await axios.post('http://127.0.0.1:5000/train/classification', formData);
      if (response.data.error) {
        setError(response.data.error);
      } else {
        setAccuracy(response.data.accuracy);
        setPrecision(response.data.precision);
        setRecall(response.data.recall);
        setF1Score(response.data.f1_score);
        setConfusionMatrix(response.data.confusion_matrix);
        setRocAuc(response.data.roc_auc);
        setClassNames(response.data.class_names);
        const pathParts = response.data.model_path.split('\\');
        const filenameWithExtension = pathParts[pathParts.length - 1];
        const modelName = filenameWithExtension.replace('_classifier_pipeline.pkl', '');
        setDownloadUrl(modelName);
      }
    } catch (error) {
      setError('Error training classification model.');
      console.error('Error training classification model:', error);
    }
    setIsTraining(false);
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
            Train Classification Model
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
            } ${file ? "border-green-500 bg-green-50" : ""}`}
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
                handleFileUpload({ target: { files: [file] } });
              }
            }}
          >
            {file ? (
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
              onChange={handleFileUpload}
            />
          </div>
        </div>

        {columns.length > 0 && (
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
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
          >
            <option value="">-- Select Model --</option>
            {models.map((model, index) => (
              <option key={index} value={model}>
                {model}
              </option>
            ))}
          </select>
        </div>

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
            placeholder='{"C": 1.0, "penalty": "l2"}'
            value={hyperparams}
            onChange={(e) => setHyperparams(e.target.value)}
            rows="4"
          />
        </div>

        <button
          onClick={handleTrain}
          disabled={isTraining || !file || !selectedModel || !targetColumn}
          className={`w-full py-3 rounded-lg font-semibold transition-colors ${
            isTraining || !file || !selectedModel || !targetColumn
              ? "bg-gray-500 cursor-not-allowed"
              : "bg-blue-500 hover:bg-blue-600"
          }`}
        >
          {isTraining ? 'Training...' : 'Train Model'}
        </button>

        {accuracy !== null && (
          <div className="mt-6 p-4 rounded-lg bg-green-50 border border-green-500">
            <h3 className="font-semibold mb-2">Evaluation Metrics:</h3>
            <p>Accuracy: {accuracy.toFixed(4)}</p>
            {precision !== null && <p>Precision: {precision.toFixed(4)}</p>}
            {recall !== null && <p>Recall: {recall.toFixed(4)}</p>}
            <p>F1-Score: {f1Score.toFixed(4)}</p>
            {rocAuc !== null && <p>ROC AUC: {rocAuc.toFixed(4)}</p>}
            {confusionMatrix && classNames.length > 0 && (
              <div className="mt-4">
                <h4 className="font-semibold mb-2">Confusion Matrix:</h4>
                <div className="overflow-x-auto">
                  <table className="table-auto border-collapse border border-gray-500">
                    <thead>
                      <tr>
                        <th className="border border-gray-500 px-4 py-2">Predicted</th>
                        {classNames.map((className) => (
                          <th key={className} className="border border-gray-500 px-4 py-2">{className}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {confusionMatrix.map((row, index) => (
                        <tr key={index}>
                          <td className="border border-gray-500 px-4 py-2 font-semibold">Actual {classNames[index]}</td>
                          {row.map((value, colIndex) => (
                            <td key={colIndex} className="border border-gray-500 px-4 py-2 text-center">{value}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
            {downloadUrl && (
              <div className="mt-4">
                <a
                  href={`http://127.0.0.1:5000/download/classification/${downloadUrl}`}
                  className="inline-block bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                  download={`trained_classification_model_${selectedModel}.pkl`}
                >
                  Download Model
                </a>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ClassificationModelPage;