import React from "react";
import TrainModel from "./Pages/TrainModel.jsx";
import { useNavigate } from "react-router-dom";

const MLSection = () => {
  const navigate = useNavigate();
  return (
    <section className="bg-gradient-to-r from-blue-900 to-indigo-900 py-20 px-6 text-white">
      <div className="container mx-auto flex flex-col lg:flex-row items-center justify-between gap-10">
        {/* Left Side: Image or Animation */}
        <div className="w-full lg:w-1/2 flex justify-center">
          <img
            src="https://cdn.pixabay.com/photo/2021/08/04/13/06/software-developer-6521720_1280.jpg"
            alt="Machine Learning"
            className="rounded-lg shadow-2xl w-full max-w-md hover:scale-105 transition-transform duration-300"
          />
        </div>

        {/* Right Side: Description and Button */}
        <div className="w-full lg:w-1/2 space-y-6">
          <h2 className="text-4xl font-bold">
            Train Machine Learning Models Online
          </h2>
          <p className="text-lg text-gray-300">
            Harness the power of Machine Learning with our intuitive platform.
            Upload your dataset, choose from a variety of algorithms, and train
            models effortlessly. Whether you're a beginner or an expert, our
            tools make it easy to build and deploy ML models.
          </p>
          <button
      onClick={() => navigate("/ml")}
      className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-3 px-6 rounded-lg shadow-lg transition-all duration-300 transform hover:scale-105 hover:cursor-pointer"
    >
            Go to ML Box
          </button>
        </div>
      </div>
    </section>
  );
};

export default MLSection;