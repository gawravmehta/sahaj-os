"use client";

import React, { createContext, useContext, useState } from "react";
import { cn } from "@/lib/utils";

const TabsContext = createContext(undefined);

export function Tabs({
  defaultValue,
  value,
  onValueChange,
  className,
  children,
}) {
  const isControlled = value !== undefined;
  const [uncontrolledValue, setUncontrolledValue] = useState(
    defaultValue || ""
  );

  const activeTab = isControlled ? value : uncontrolledValue;

  const setActiveTab = (val) => {
    if (!isControlled) setUncontrolledValue(val);
    onValueChange?.(val);
  };

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className={cn("w-full", className)}>{children}</div>
    </TabsContext.Provider>
  );
}

export function TabsList({ children, className }) {
  return <div className={cn("flex flex-wrap", className)}>{children}</div>;
}

export function TabsTrigger({
  value,
  variant = "primary",
  className,
  children,
}) {
  const context = useContext(TabsContext);
  if (!context) throw new Error("TabsTrigger must be used inside <Tabs>");

  const isActive = context.activeTab === value;

  const baseStyle =
    "px-4 py-2 text-sm font-medium capitalize transition-all duration-300 ease-in-out cursor-pointer";

  const primary = isActive
    ? "bg-primary text-white"
    : "text-gray-600 hover:bg-primary hover:text-white";

  const secondary =
    "text-gray-500 hover:text-primary border-b-2 border-primary py-3";

  const styles = cn(
    baseStyle,
    variant === "primary" ? primary : secondary,
    className
  );

  const inlineStyle =
    variant === "secondary" && !isActive
      ? {
          borderColor: "rgba(59, 130, 246, 0)",
          transition: "border-color 0.3s",
        }
      : {};

  return (
    <button
      className={styles}
      style={inlineStyle}
      onClick={() => context.setActiveTab(value)}
    >
      {children}
    </button>
  );
}

export function TabsContent({ value, children, className }) {
  const context = useContext(TabsContext);
  if (!context) throw new Error("TabsContent must be used inside <Tabs>");

  if (context.activeTab !== value) return null;

  return <div className={cn(className)}>{children}</div>;
}
