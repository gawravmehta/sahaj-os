"use client";

import { useState, useEffect } from "react";

export default function ToggleButton({
  checked,
  revokeConsent,
  consect_id,
  setConsect,
  consect,
}) {
  const [isToggled, setIsToggled] = useState(checked);

  const toggleSwitch = () => {
    setConsect(consect_id);
    if (consect && isToggled) {
      revokeConsent();
      setIsToggled(!isToggled);
    }
  };

  useEffect(() => {
    setIsToggled(checked);
  }, [checked]);

  return (
    <button
      onClick={toggleSwitch}
      className={`${
        isToggled ? "bg-blue-600" : "bg-gray-300"
      } relative inline-flex items-center h-6 rounded-full w-11 transition-colors duration-300 ease-in-out`}
    >
      <span
        className={`${
          isToggled ? "translate-x-6" : "translate-x-1"
        } inline-block w-4 h-4 transform bg-white rounded-full transition-transform duration-300 ease-in-out`}
      />
    </button>
  );
}
