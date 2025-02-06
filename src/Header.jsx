import React, { useState } from "react";
import logo from "./assets/logo.jpg"

const Header = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const scrollToSection = (id) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <header className="sticky top-0 z-50 w-full bg-black backdrop-blur-sm text-white shadow-lg">
      <div className="container mx-auto px-6 py-4">
        <div className="flex justify-between items-center">
          {/* Logo */}
          <h1 className="font-montserrat text-2xl font-bold">
            <a href="#" className="hover:opacity-80 transition-opacity duration-300 flex items-center">
              <img src={logo} alt="Phy Box Logo" className="h-12 w-auto" />
              <span className="ml-4">
                <span className="text-blue-400">Phy</span>
                <span className="text-white">Box</span>
              </span>
            </a>
          </h1>


          {/* Desktop Navigation */}
          <div className="flex items-center gap-8">
            <nav className="flex-1 flex justify-center items-center gap-8 max-lg:hidden">
              <ul className="flex space-x-8">
                <li>
                <a
                    href="#home"
                    onClick={(e) => {
                      e.preventDefault();
                      scrollToSection("home");
                    }}
                    className="text-lg font-medium hover:text-blue-200 transition-colors duration-300 relative group"
                  >
                    <i className="fa-solid fa-house mr-2"></i>
                    Home
                    <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-blue-200 transition-all duration-300 group-hover:w-full"></span>
                  </a>
                </li>
                <li>
                  <a
                    href="#ml-box"
                    onClick={(e) => {
                      e.preventDefault();
                      scrollToSection("ml-box");
                    }}
                    className="text-lg font-medium hover:text-blue-200 transition-colors duration-300 relative group"
                  >
                    <i className="fa-solid fa-robot mr-2"></i>
                    ML Box
                    <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-blue-200 transition-all duration-300 group-hover:w-full"></span>
                  </a>
                </li>
                <li>
                  <a
                    href="#simulation"
                    onClick={(e) => {
                      e.preventDefault();
                      scrollToSection("simulation");
                    }}
                    className="text-lg font-medium hover:text-blue-200 transition-colors duration-300 relative group"
                  >
                    <i className="fa-solid fa-cube mr-2"></i>
                    Simulation
                    <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-blue-200 transition-all duration-300 group-hover:w-full"></span>
                  </a>
                </li>
                <li>
                  <a
                    href="#tutor"
                    onClick={(e) => {
                      e.preventDefault();
                      scrollToSection("tutor");
                    }}
                    className="text-lg font-medium hover:text-blue-200 transition-colors duration-300 relative group"
                  >
                    <i className="fa-solid fa-chalkboard-user mr-2"></i>
                    Tutor
                    <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-blue-200 transition-all duration-300 group-hover:w-full"></span>
                  </a>
                </li>
               
                <li>
                  <a
                    href="#tutor"
                    onClick={(e) => {
                      e.preventDefault();
                      scrollToSection("tutor");
                    }}
                    className="text-lg font-medium hover:text-blue-200 transition-colors duration-300 relative group"
                  >
                    <i class="fa-solid fa-address-card mr-2"></i> 
                      About
                    <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-blue-200 transition-all duration-300 group-hover:w-full"></span>
                  </a>
                </li>
              </ul>
            </nav>
            
          </div>

          {/* Mobile Menu Toggle */}
          <div className="lg:hidden">
            <button
              onClick={toggleMobileMenu}
              className="p-2 focus:outline-none"
            >
              <i className="fa-solid fa-bars text-2xl"></i>
            </button>
          </div>
        </div>

        {/* Mobile Navigation Menu */}
        
            {isMobileMenuOpen && (
              <div className="lg:hidden mt-4 animate-menuSlideIn">
                <ul className="flex flex-col space-y-4">
                  {["home", "simulation", "tutor", "ml-box"].map((section, index) => (
                    <li 
                      key={section}
                      className="opacity-0 animate-menuItemFade"
                      style={{ animationDelay: `${index * 0.1}s` }}
                    >
                      <a
                        href={`#${section}`}
                        onClick={(e) => {
                          e.preventDefault();
                          scrollToSection(section);
                          toggleMobileMenu();
                        }}
                        className="block text-lg font-medium hover:text-blue-200 transition-all duration-300 transform hover:translate-x-2"
                      >
                        {section.charAt(0).toUpperCase() + section.slice(1)}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            </div>


    </header>
  );
};

export default Header;