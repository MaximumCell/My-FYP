const [recommendedModel, setRecommendedModel] = useState("");

const handleFileUpload = async (e) => {
  const file = e.target.files[0];
  setFile(file);

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await axios.post("http://127.0.0.1:5000/recommend", formData);
    setRecommendedModel(response.data.recommended_model);
  } catch (error) {
    console.error("Error recommending model:", error);
  }
};

return (
  <div>
    <input type="file" onChange={handleFileUpload} />
    {recommendedModel && (
      <p className="mt-2 text-green-500">
        🔹 Recommended Model: <strong>{recommendedModel}</strong>
      </p>
    )}
  </div>
);
