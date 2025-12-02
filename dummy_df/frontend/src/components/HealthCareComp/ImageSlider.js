"use client";

import Image from "next/image";
import React, { useState, useEffect } from "react";
import { GoDotFill } from "react-icons/go";

const ImageSlider = () => {
  const [currentIndex, setCurrentIndex] = useState(0);

  const images = [
    "https://stgaccinwbsdevlrs01.blob.core.windows.net/newcorporatewbsite/homepage-banners/July2024/LHix0in9BVpgsOrnQHvR.webp?w=1920&q=75",
    "https://stgaccinwbsdevlrs01.blob.core.windows.net/newcorporatewbsite/homepage-banners/January2024/CCeVjCKszDYpK1Zw5MPj.webp?w=1920&q=75",
    "https://stgaccinwbsdevlrs01.blob.core.windows.net/newcorporatewbsite/homepage-banners/January2024/VN8DnbFlModceGUJm44g.webp?w=1920&q=75",
  ];

  const showSlide = (index) => {
    if (index >= images.length) {
      setCurrentIndex(0);
    } else if (index < 0) {
      setCurrentIndex(images.length - 1);
    } else {
      setCurrentIndex(index);
    }
  };

  const nextSlide = () => {
    showSlide(currentIndex + 1);
  };

  const prevSlide = () => {
    showSlide(currentIndex - 1);
  };

  // Automatically switch to the next slide every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      nextSlide();
    }, 5000); // 5000ms = 5 seconds

    return () => clearInterval(interval); // Cleanup on component unmount
  }, [currentIndex]);

  return (
    <div className="relative w-full overflow-x-hidden mt-[70px]">
      <div
        className="flex transition-transform duration-500 h-full object-fill"
        style={{ transform: `translateX(${-currentIndex * 100}%)` }}
      >
        {images.map((src, index) => (
          <Image
            key={index}
            src={src}
            alt={`Slide ${index + 1}`}
            height={1400}
            width={1400}
            className="w-full object-fill bg-cover bg-slate-800 "
          />
        ))}
      </div>

      {/* Navigation buttons (commented out) */}
      {/* <button
        className="absolute left-4 top-1/2 transform -translate-y-1/2 bg-gray-800 bg-opacity-50 text-white p-2 rounded-full hover:bg-gray-900"
        onClick={prevSlide}
      >
        &#10094;
      </button>
      <button
        className="absolute right-4 top-1/2 transform -translate-y-1/2 bg-gray-800 bg-opacity-50 text-white p-2 rounded-full hover:bg-gray-900"
        onClick={nextSlide}
      >
        &#10095;
      </button> */}

      {/* Dots for navigation */}
      <div className="flex absolute bottom-5 left-1/2 transform -translate-x-1/2 space-x-2">
        {images.map((item, index) => (
          <span
            key={index}
            className={`cursor-pointer ${
              index === currentIndex ? "text-white" : "text-gray-500"
            }`}
            onClick={() => showSlide(index)}
          >
            <GoDotFill size={24} />
          </span>
        ))}
      </div>
    </div>
  );
};

export default ImageSlider;
