import Footer from "./Footer.jsx";
import Header from "./Header.jsx";
import MLSection from "./MLSection.jsx";
import About from "./components/About.jsx";
import Hero from "./Hero.jsx";
import Carousel from "./components/Carousel.jsx";
import MathAI from "./components/MathAI.jsx";

export const Home = () => {
  return (
    <main className="min-h-screen bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100">
      <Header />

      {/* Fullscreen carousel hero
      <section id="home" className="w-full h-screen">
        <Carousel />
      </section> */}

      {/* Brief intro under carousel */}
      <section id="intro" className="w-full mx-auto px-0 py-0">
        <Hero />
      </section>
      <section id="ml-box">
        <MLSection />
      </section>

      <section id="tutor" >
        <MathAI />
      </section>

      <section id="About">
        <About />
      </section>

      <Footer />
    </main>
  );
};
