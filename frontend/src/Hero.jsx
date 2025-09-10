import React from "react";
import Carousel from "./components/Carousel";
const Hero = () => {
  return (
    <section className="w-full overflow-hidden flex xl:flex-row flex-col justify-center min-h-screen gap-10">
      <div className="relative flex justify-center items-start w-full">
        <Carousel />
      </div>
    </section>
  );
};

export default Hero;
