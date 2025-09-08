import React from "react";
import mathAIImg from "../assets/mathai.jpg"; // Import local image for Math AI

const MathAI = () => {
  return (
    <section className="bg-gradient-to-r from-green-900 to-teal-900 py-20 px-6 text-white">
      <div className="container mx-auto flex flex-col lg:flex-row items-center justify-between gap-10">
        {/* Left Side: Image or Animation */}
        <div className="w-full lg:w-1/2 flex justify-center">
          <img
            src={mathAIImg} // Use local image
            alt="Math AI for Physics Students"
            className="rounded-lg shadow-2xl w-full max-w-md hover:scale-105 transition-transform duration-300"
            onError={(e) => {
              console.error("Image failed to load:", e.target.src);
              e.target.src = "https://via.placeholder.com/500x300"; // Fallback image
            }}
          />
        </div>

        {/* Right Side: Description and Button */}
        <div className="w-full lg:w-1/2 space-y-6">
          <h2 className="text-4xl font-bold">
            Solve Physics Math Problems with AI
          </h2>
          <p className="text-lg text-gray-300">
            Struggling with complex math in physics? Our Math AI tool is here to
            help! Whether it's solving differential equations, linear algebra, or
            calculus-based physics problems, our AI-powered platform provides
            step-by-step solutions tailored for physics students.
          </p>
          <button
            onClick={() => {
              // Redirect to Math AI Tool
              window.location.href = "/math-ai-tool";
            }}
            className="bg-green-500 hover:bg-green-600 text-white font-semibold py-3 px-6 rounded-lg shadow-lg transition-all duration-300 transform hover:scale-105"
          >
            Go to Math AI Tool
          </button>
        </div>
      </div>
    </section>
  );
};

export default MathAI;