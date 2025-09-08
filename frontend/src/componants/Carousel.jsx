import { Swiper, SwiperSlide } from "swiper/react";
import "swiper/css";
import "swiper/css/pagination";
import "swiper/css/navigation";
import { Pagination, Navigation, Autoplay } from "swiper/modules";
import { useRef, useState } from "react";
import ML from "../assets/ML.jpg";
import phsim from "../assets/phsim.jpg";
import mathai from "../assets/mathai.jpg";

const Carousel = () => {
  const options = [
    { title: "Machine Learning", desc: "Train models with data", img: ML, link: "/machine-learning" },
    { title: "Simulation", desc: "Physics-based interactive simulations", img: phsim, link: "/simulation" },
    { title: "Math AI", desc: "Solve equations with AI", img: mathai, link: "/math-ai" },
  ];

  const swiperRef = useRef(null);
  const [prevHover, setPrevHover] = useState(false);
  const [nextHover, setNextHover] = useState(false);

  return (
    <div className="relative w-full h-screen">
      <Swiper
        ref={swiperRef}
        modules={[Pagination, Navigation, Autoplay]}
        spaceBetween={0}
        slidesPerView={1}
        pagination={{ clickable: true }}
        navigation={{ prevEl: ".prev-btn", nextEl: ".next-btn" }}
        loop={true}
        autoplay={{ delay: 5000, disableOnInteraction: false }} // Each slide stays for 5 seconds
        className="w-full h-full"
      >
        {options.map((item, index) => (
          <SwiperSlide key={index}>
            <div className="relative w-full h-screen">
              <img src={item.img} alt={item.title} className="w-full h-full object-cover" />
              <div className="absolute inset-0 flex items-center justify-start p-10">
                <div className="text-white max-w-lg bg-opacity-50 backdrop-blur-md p-8 rounded-lg">
                  <h2 className="text-4xl font-bold">{item.title}</h2>
                  <p className="text-lg mt-2">{item.desc}</p>
                  <a href={item.link} className="mt-4 inline-block bg-blue-500 text-white px-6 py-2 rounded-lg hover:bg-blue-600 transition-colors duration-300">
                    Go to {item.title}
                  </a>
                </div>
              </div>
            </div>
          </SwiperSlide>
        ))}
      </Swiper>

      {/* Improved Navigation Buttons */}
      <button
        className={`prev-btn absolute left-5 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white w-12 h-12 flex items-center justify-center rounded-lg shadow-md transition-opacity duration-300 z-50 ${
          prevHover ? "opacity-100" : "opacity-0"
        }`}
        onMouseEnter={() => setPrevHover(true)}
        onMouseLeave={() => setPrevHover(false)}
      >
        &lt;
      </button>
      <button
        className={`next-btn absolute right-5 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-0 text-white w-12 h-12 flex items-center justify-center rounded-lg shadow-md transition-opacity duration-300 z-50 ${
          nextHover ? "opacity-100" : "opacity-0"
        }`}
        onMouseEnter={() => setNextHover(true)}
        onMouseLeave={() => setNextHover(false)}
      >
        &gt;
      </button>
    </div>
  );
};

export default Carousel;