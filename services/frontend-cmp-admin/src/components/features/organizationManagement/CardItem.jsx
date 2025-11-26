"use client";
import Image from "next/image";
import React from "react";

const CardItem = ({ index, title, icon, count, activeCard, onClick }) => {
  const isActive = activeCard === index;

  return (
    <div className="w-full">
      <div
        className={`cursor-pointer border  p-4 shadow-sm transition-all duration-300 ${
          isActive
            ? "border-primary  shadow-md"
            : "border-gray-200 bg-white hover:shadow-md"
        }`}
        onClick={() => onClick(index)}
      >
        <div className="flex flex-col justify-between gap-4 mb-2">
          <div className="flex items-center justify-between">
            <div className="w-16 h-16">
              <Image
                src={icon}
                alt={title}
                width={64}
                height={64}
                className="w-full h-full object-contain"
              />
            </div>
            {typeof count !== "undefined" && (
              <div className="text-[30px] font-medium text-primary px-3 py-1">
                {count}
              </div>
            )}
          </div>
          <h3 className="text-[20px]  text-heading">{title}</h3>
        </div>
      </div>
    </div>
  );
};

export default CardItem;
