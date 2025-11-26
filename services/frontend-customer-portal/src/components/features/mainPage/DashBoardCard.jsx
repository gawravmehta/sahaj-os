import Image from "next/image";
import React from "react";

const DashboardCard = ({ title, description, onClick, isActive, image }) => {
  return (
    <div
      onClick={onClick}
      className={`cursor-pointer p-7  border relative hover:bg-gray-50 ${
        isActive ? "bg-gray-100" : "bg-transparent"
      }`}
    >
      <div className="w-1/2">
        <div className="text-lg font-semibold">{title}</div>
        <div className="text-xs text-gray-600">{description}</div>
      </div>
    </div>
  );
};

export default DashboardCard;
