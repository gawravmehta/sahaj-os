import Link from "next/link";
import React from "react";
import { FaArrowRightLong } from "react-icons/fa6";

const ExpertiseCard = () => {
  return (
    <div className=" bg-[#F7F9F9] py-10">
      <div className="">
        <h1 className="text-4xl my-5  font-medium text-center">
          Expert Care Nationwide
        </h1>
        <p className=" text-center font-medium text-[#565454] w-[70%] m-auto text-lg">
          Our expert doctors provide specialized care across 21 hospitals
          nationwide, covering 110+ specialties such as cardiac sciences, cancer
          care, orthopaedics, neurology, gastroenterology, liver and kidney
          transplants etc.
        </p>
      </div>
      <div className="flex gap-8 justify-center py-10 w-[85%] m-auto">
        <div
          className="relative w-80 h-96 bg-cover bg-center group overflow-hidden rounded-lg shadow-lg text-white"
          style={{
            backgroundImage:
              "url('https://stgaccinwbsdevlrs01.blob.core.windows.net/newcorporatewbsite/specialities/March2024/A2usSrvhV7nhhAahWwbq.webp?w=640&q=75')",
          }}
        >
          <div className="absolute inset-0 transition duration-300 opacity-65 group-hover:bg-blue-800"></div>
          <div className="absolute inset-0 transition duration-300 opacity-65 bg-[#F7F9F9] group-hover:opacity-0 "></div>

          <h3 className=" absolute text-blue-900 group-hover:text-white top-1/2 w-1/2 pl-7 pt-5 transform -translate-y-1/2 group-hover:top-0 group-hover:translate-y-0 transition-all duration-700 ease-in-out text-2xl font-bold z-10">
            Cardiac Sciences
          </h3>

          <div className="absolute inset-0 flex flex-col justify-end p-7 opacity-0 group-hover:opacity-100 transition-opacity duration-200 ease-in-out z-20">
            <span className="w-full">
              <p className="text-sm mb-4 transform -translate-x-full group-hover:translate-x-0 transition-transform duration-500 ease-in-out">
                At Narayana Health, we&apos;ve been the pioneers in heart care since
                2000. We&apos;re known worldwide for treating complex heart problems.
              </p>
              <Link
                href="#"
                className="flex items-center justify-between transform -translate-x-full group-hover:translate-x-0 transition-transform duration-500 ease-in-out"
              >
                Read More
                <FaArrowRightLong size={30} />
              </Link>
            </span>
          </div>
        </div>

        <div
          className="relative w-80 h-96 bg-cover bg-center group overflow-hidden rounded-lg shadow-lg text-white"
          style={{
            backgroundImage:
              "url('https://stgaccinwbsdevlrs01.blob.core.windows.net/newcorporatewbsite/specialities/March2024/cjdtUDLeiMSYaPYsPynR.webp?w=384&q=75')",
          }}
        >
          <div className="absolute inset-0 transition duration-300 opacity-65 group-hover:bg-blue-800"></div>
          <div className="absolute inset-0 transition duration-300 opacity-65 bg-[#F7F9F9] group-hover:opacity-0 "></div>

          <h3 className="absolute text-blue-900 group-hover:text-white top-1/2 w-1/2 pl-7 pt-5 transform -translate-y-1/2 group-hover:top-0 group-hover:translate-y-0 transition-all duration-700 ease-in-out text-2xl font-bold z-10">
            Cancer Care
          </h3>

          <div className="absolute inset-0 flex flex-col justify-end p-7 opacity-0 group-hover:opacity-100 transition-opacity duration-300 ease-in-out z-20">
            <span className="w-full">
              <p className="text-sm mb-4 transform -translate-x-full group-hover:translate-x-0 transition-transform duration-500 ease-in-out">
                We lead in oncology services, blending expertise, compassion,
                and a legacy of healthcare excellence.
              </p>
              <Link
                href="#"
                className="flex items-center justify-between transform -translate-x-full group-hover:translate-x-0 transition-transform duration-500 ease-in-out"
              >
                Read More
                <FaArrowRightLong size={30} />
              </Link>
            </span>
          </div>
        </div>

        <div
          className="relative w-80 h-96 bg-cover bg-center group overflow-hidden rounded-lg shadow-lg text-white"
          style={{
            backgroundImage:
              "url('https://stgaccinwbsdevlrs01.blob.core.windows.net/newcorporatewbsite/specialities/March2024/7PUBN9ygZaIgJlxE38Jv.webp?w=384&q=75')",
          }}
        >
          <div className="absolute inset-0 transition duration-300 opacity-65 group-hover:bg-blue-800"></div>
          <div className="absolute inset-0 transition duration-300 opacity-65 bg-[#F7F9F9] group-hover:opacity-0 "></div>

          <h3 className="absolute text-blue-900 group-hover:text-white top-1/2 w-1/2 pl-7 pt-5 transform -translate-y-1/2 group-hover:top-0 group-hover:translate-y-0 transition-all duration-700 ease-in-out text-2xl font-bold z-10">
            Neuro Sciences
          </h3>

          <div className="absolute inset-0 flex flex-col justify-end p-7 opacity-0 group-hover:opacity-100 transition-opacity duration-300 ease-in-out z-20">
            <span className="w-full">
              <p className="text-sm mb-4 transform -translate-x-full group-hover:translate-x-0 transition-transform duration-500 ease-in-out">
                We specialize in Neurosciences, with dedicated teams for adult
                and pediatric neurosurgery and neurology.
              </p>
              <Link
                href="#"
                className="flex items-center justify-between transform -translate-x-full group-hover:translate-x-0 transition-transform duration-500 ease-in-out"
              >
                Read More
                <FaArrowRightLong size={30} />
              </Link>
            </span>
          </div>
        </div>

        <div
          className="relative w-80 h-96 bg-cover bg-center group overflow-hidden rounded-lg shadow-lg text-white"
          style={{
            backgroundImage:
              "url('https://stgaccinwbsdevlrs01.blob.core.windows.net/newcorporatewbsite/specialities/March2024/vneMY8PUJbE32Hh4WB2C.webp?w=384&q=75')",
          }}
        >
          <div className="absolute inset-0 transition duration-300 opacity-65 group-hover:bg-blue-800"></div>
          <div className="absolute inset-0 transition duration-300 opacity-65 bg-[#F7F9F9] group-hover:opacity-0 "></div>

          <h3 className="absolute text-blue-900 group-hover:text-white top-1/2 w-1/2 pl-7 pt-5 transform -translate-y-1/2 group-hover:top-0 group-hover:translate-y-0 transition-all duration-700 ease-in-out text-2xl font-bold z-10">
            Gastro Sciences
          </h3>

          <div className="absolute inset-0 flex flex-col justify-end p-7 opacity-0 group-hover:opacity-100 transition-opacity duration-300 ease-in-out z-20">
            <span className="w-full">
              <p className="text-sm mb-4 transform -translate-x-full group-hover:translate-x-0 transition-transform duration-500 ease-in-out">
                With expert doctors specializing in all areas of gastrosciences,
                we offer treatment and care for adults and children.
              </p>
              <Link
                href="#"
                className="flex items-center justify-between transform -translate-x-full group-hover:translate-x-0 transition-transform duration-500 ease-in-out"
              >
                Read More
                <FaArrowRightLong size={30} />
              </Link>
            </span>
          </div>
        </div>

        <div
          className="relative w-80 h-96 bg-cover bg-center group overflow-hidden rounded-lg shadow-lg text-white"
          style={{
            backgroundImage:
              "url('https://stgaccinwbsdevlrs01.blob.core.windows.net/newcorporatewbsite/specialities/March2024/hkBHnsy9RX8ByAAr4GfJ.webp?w=384&q=75')",
          }}
        >
          <div className="absolute inset-0 transition duration-300 opacity-65 group-hover:bg-blue-800"></div>
          <div className="absolute inset-0 transition duration-300 opacity-65 bg-[#F7F9F9] group-hover:opacity-0 "></div>

          <h3 className="absolute text-blue-900 group-hover:text-white top-1/2 w-1/2 pl-7 pt-5 transform -translate-y-1/2 group-hover:top-0 group-hover:translate-y-0 transition-all duration-700 ease-in-out text-2xl font-bold z-10">
            Orthopaedics
          </h3>

          <div className="absolute inset-0 flex flex-col justify-end p-7 opacity-0 group-hover:opacity-100 transition-opacity duration-300 ease-in-out z-20">
            <span className="w-full">
              <p className="text-sm mb-4 transform -translate-x-full group-hover:translate-x-0 transition-transform duration-500 ease-in-out">
                As one of the top orthopaedic hospitals in India, we&apos;ve served
                thousands over two decades, delivering quality healthcare.
              </p>
              <Link
                href="#"
                className="flex items-center justify-between transform -translate-x-full group-hover:translate-x-0 transition-transform duration-500 ease-in-out"
              >
                Read More
                <FaArrowRightLong size={30} />
              </Link>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ExpertiseCard;
