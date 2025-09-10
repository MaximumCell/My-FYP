import React from "react";

export default function Button({
  children,
  variant = "primary",
  className = "",
  ...props
}) {
  const base = "px-4 py-2 rounded-md font-semibold transition";
  const styles =
    variant === "primary"
      ? "bg-brand-500 text-white hover:bg-brand-700"
      : "border bg-transparent text-slate-800 dark:text-slate-100";
  return (
    <button className={`${base} ${styles} ${className}`} {...props}>
      {children}
    </button>
  );
}
