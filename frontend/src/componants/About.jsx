import React from "react";
import Ai_me from "../assets/Ai_me.jpg";

const About = () => {
  return (
    <section className="bg-gradient-to-r bg-gray-700 to-teal-900 py-20 px-6 text-white">
      <div className="container mx-auto flex flex-col lg:flex-row items-center justify-between gap-10">
        {/* Left Side: Description and Button */}
        <div className="w-full lg:w-1/2 space-y-6">
          <h2 className="text-4xl font-bold">About</h2>
          <p className="text-lg text-gray-300">
            We are dedicated to providing innovative solutions for students and
            professionals in physics, math, and machine learning.
          </p>
        </div>

        {/* Right Side: Image or Animation */}
        <div className="w-full lg:w-1/2 flex justify-center">
          <img
            src={Ai_me}
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

export default About;
