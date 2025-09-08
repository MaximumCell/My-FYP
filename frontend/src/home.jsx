import Footer from "./Footer.jsx";
import Header from "./Header.jsx";
import Hero from "./Hero.jsx";
import MLSection from "./MLSection.jsx";
import About from "./componants/About.jsx";
import MathAI from "./componants/MathAi.jsx";
import Simulation from "./componants/Simulation.jsx";


const home = () => {
  return (
    <>
      <main>
        <Header />
        <section id="home" className="scroll-mt-25">
          <Hero />
        </section>
        <section id="ml-box" className="scroll-mt-25">
          <MLSection />
        </section>
        <section id="simulation" className="scroll-mt-25">
          <Simulation />
        </section>
        <section id="tutor" className="scroll-mt-25">
          <MathAI />
        </section>
        <section id="About" className="scroll-mt-10">
          <About />
        </section>
        <Footer />
      </main>
    </>
  )
}

export default home