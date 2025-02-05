import React, { useState } from "react";

const Header = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  return (
    <header className="sticky top-0 z-50 w-full bg-black text-white shadow-lg">
      <div className="container mx-auto px-6 py-4">
        <div className="flex justify-between items-center">
          {/* Logo */}
          <h1 className="font-montserrat text-2xl font-bold">
            <a href="#" className="hover:text-blue-200 transition-colors duration-300">
              Phy Box
            </a>
          </h1>

          {/* Desktop Navigation */}
          <nav className="flex-1 flex justify-center items-center gap-8 max-lg:hidden">
            <ul className="flex space-x-8">
              <li>
                <a
                  href="#"
                  className="text-lg font-medium hover:text-blue-200 transition-colors duration-300"
                >
                  Home
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-lg font-medium hover:text-blue-200 transition-colors duration-300"
                >
                  Simulation
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-lg font-medium hover:text-blue-200 transition-colors duration-300"
                >
                  Tutor
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="text-lg font-medium hover:text-blue-200 transition-colors duration-300"
                >
                  ML Box
                </a>
              </li>
            </ul>
          </nav>

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
          <div className="lg:hidden mt-4">
            <ul className="flex flex-col space-y-4">
              <li>
                <a
                  href="#"
                  className="block text-lg font-medium hover:text-blue-200 transition-colors duration-300"
                >
                  Home
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="block text-lg font-medium hover:text-blue-200 transition-colors duration-300"
                >
                  Simulation
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="block text-lg font-medium hover:text-blue-200 transition-colors duration-300"
                >
                  Tutor
                </a>
              </li>
              <li>
                <a
                  href="#"
                  className="block text-lg font-medium hover:text-blue-200 transition-colors duration-300"
                >
                  ML Box
                </a>
              </li>
            </ul>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;