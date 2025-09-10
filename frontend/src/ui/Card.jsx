import React from "react";

export default function Card({ children, className = "" }) {
  return (
    <div
      className={`rounded-lg shadow-md p-6 bg-white dark:bg-slate-800 ${className}`}
    >
      {children}
    </div>
  );
}
