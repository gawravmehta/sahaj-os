"use client";

import React from "react";

const CheckboxGroup = ({ label, options, selectedValues, onChange }) => {
  const handleCheckboxChange = (event) => {
    const { value, checked } = event.target;
    if (checked) {
      onChange([...selectedValues, value]);
    } else {
      onChange(selectedValues.filter((item) => item !== value));
    }
  };

  return (
    <div className="flex flex-col gap-2">
      {label && <label className="text-sm font-medium text-gray-700">{label}</label>}
      <div className="grid grid-cols-2 gap-2">
        {options.map((option) => (
          <div key={option} className="flex items-center">
            <input
              type="checkbox"
              id={option}
              name={option}
              value={option}
              checked={selectedValues.includes(option)}
              onChange={handleCheckboxChange}
              className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            />
            <label htmlFor={option} className="ml-2 text-sm text-gray-900">
              {option}
            </label>
          </div>
        ))}
      </div>
    </div>
  );
};

export default CheckboxGroup;
