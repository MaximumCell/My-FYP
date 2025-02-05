import Footer from "./Footer.jsx";
import Header from "./Header.jsx";
import Hero from "./Hero.jsx";
import MLSection from "./MLSection.jsx";
import MathAI from "./componants/MathAi.jsx";
import Simulation from "./componants/Simulation.jsx";

function App() {

  return (
    <>
      <main>
        <Header />
          <section id="home">
          <Hero />
          </section>
          <section id="ml-box">
          <MLSection />
          </section>
          <section id="simulation">
          <Simulation />
          </section>

          <section id="tutor">
          <MathAI />
          </section>
          <Footer />



      </main>
    </>
  )
}

export default App
