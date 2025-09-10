import React, { useEffect, useState } from "react";
import { Sun, Moon } from "lucide-react";

const getInitialTheme = () => {
  if (typeof window === "undefined") return "light";
  const saved = localStorage.getItem("theme");
  if (saved) return saved;
  return window.matchMedia &&
    window.matchMedia("(prefers-color-scheme: dark)").matches
    ? "dark"
    : "light";
};

export default function ThemeToggle() {
  const [theme, setTheme] = useState(getInitialTheme);

  useEffect(() => {
    const root = document.documentElement;
    if (theme === "dark") {
      root.classList.add("dark");
    } else {
      root.classList.remove("dark");
    }
    localStorage.setItem("theme", theme);
  }, [theme]);

  return (
    <button
      aria-label="Toggle theme"
      className="p-2 rounded-md hover:bg-gray-200/20 transition"
      onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
    >
      {theme === "dark" ? (
        <Sun className="w-5 h-5" />
      ) : (
        <Moon className="w-5 h-5" />
      )}
    </button>
  );
}
