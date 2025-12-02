"use client";
import Image from 'next/image';
import React, { useState } from 'react';

const carouselItems = [
  "https://c8.alamy.com/comp/2WPJGD3/indian-cute-bride-and-groom-cartoon-character-wedding-theme-2WPJGD3.jpg",
  "https://c8.alamy.com/compit/2wpjg8m/tema-di-nozze-dei-personaggi-dei-cartoni-animati-della-sposa-e-dello-sposo-indiano-2wpjg8m.jpg",
  "https://i.pinimg.com/736x/12/ab/6a/12ab6aa0614d6b4f7b4743b6611c3ae5.jpg",
  "https://thumbs.dreamstime.com/b/indian-newlywed-couple-ties-knot-according-to-hindu-marriage-against-indian-newlywed-couple-ties-knot-according-to-hindu-285032373.jpg",
  "https://cdn.pixabay.com/photo/2021/07/27/13/59/groom-6496931_640.png",
  "https://www.shutterstock.com/image-vector/indian-hindu-wedding-couple-vector-260nw-2139167531.jpg"
];

const CustomCarousel = () => {
  const [currentIndex, setCurrentIndex] = useState(0);

  const nextSlide = () => {
    setCurrentIndex((prevIndex) => (prevIndex + 1) % carouselItems.length);
  };

  const prevSlide = () => {
    setCurrentIndex((prevIndex) =>
      prevIndex === 0 ? carouselItems.length - 1 : prevIndex - 1
    );
  };

  return (
    <div className="py-8 px-64">
      <div className="text-center mb-8">
        <span className="text-lg text-gray-600">LAKHS OF HAPPY COUPLES</span>
        <h2 className="text-3xl font-bold mt-2">
          Matched by <span className="text-pink-500">Soul Match</span>
        </h2>
      </div>

      <div className="relative">
        <button
          onClick={prevSlide}
          className="absolute left-0 top-1/2 transform -translate-y-1/2 bg-gray-600 text-white p-2 rounded-full"
        >
          &#10094;
        </button>
        <div className="flex justify-center">
          <Image
          height={300}
          width={400}
          
            src={carouselItems[currentIndex]}
            alt="Carousel"
            className="w-56 h-56"
            
          />
        </div>
        <button
          onClick={nextSlide}
          className="absolute right-0 top-1/2 transform -translate-y-1/2 bg-gray-600 text-white p-2 rounded-full"
        >
          &#10095;
        </button>
      </div>
    </div>
  );
};

export default CustomCarousel;
