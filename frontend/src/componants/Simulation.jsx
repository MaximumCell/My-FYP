import React from "react";
import physimimg from "../assets/physimimg.jpg";
import { useNavigate } from "react-router-dom";

const Simulation = () => {
  const navigate = useNavigate();
  return (
    <section className="bg-gradient-to-r from-purple-900 to-indigo-900 py-20 px-6 text-white">
      <div className="container mx-auto flex flex-col lg:flex-row items-center justify-between gap-10">
        {/* Left Side: Description and Button */}
        <div className="w-full lg:w-1/2 space-y-6">
          <h2 className="text-4xl font-bold">
            Interactive Physics Simulations
          </h2>
          <p className="text-lg text-gray-300">
            Explore the world of physics with our interactive simulations. From
            mechanics to electromagnetism, our tools allow you to visualize and
            experiment with complex concepts in a user-friendly environment.
            Perfect for students, educators, and enthusiasts alike.
          </p>
          <button
            onClick={() => navigate("/simulation")}
            className="bg-purple-500 hover:bg-purple-600 text-white font-semibold py-3 px-6 rounded-lg shadow-lg transition-all duration-300 transform hover:scale-105"
          >
            Go to Simulation Box
          </button>
        </div>

        {/* Right Side: Image or Animation */}
        <div className="w-full lg:w-1/2 flex justify-center">
          <img
            src={physimimg}
            alt="Physics Simulation"
            className="rounded-lg shadow-2xl w-full max-w-md hover:scale-105 transition-transform duration-300"
            onError={(e) => {
              console.error("Image failed to load:", e.target.src);
              e.target.src = "fallback-image-url.jpg"; // Fallback image
            }}
          />
        </div>
      </div>
    </section>
  );
};

export default Simulation;