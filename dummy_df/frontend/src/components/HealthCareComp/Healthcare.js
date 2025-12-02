"use client";
import Image from "next/image";
import React, { useState } from "react";

const Healthcare = () => {
  const [togail, setTogail] = useState("success stories");
  return (
    <div>
      <div className=" py-10 overflow-x-hidden">
        <h1 className="text-4xl my-5  font-medium text-center">
          Expert Care Nationwide
        </h1>
        <p className=" text-center font-medium text-[#565454] text-lg">
          Read about Narayana Health&apos;s success stories, stay informed with the
          latest news and media updates, and explore informative blogs from our
          experts.
        </p>
      </div>

      <div className=" flex justify-center gap-5 pb-5">
        <button
          onClick={() => setTogail("success stories")}
          className={`py-2 px-5  rounded-md font-semibold ${
            togail === "success stories"
              ? "bg-blue-800 text-white"
              : " text-blue-800 border"
          }`}
        >
          Success Stories
        </button>
        <button
          onClick={() => setTogail("news & articles")}
          className={`py-2 px-5  rounded-md font-semibold ${
            togail === "news & articles"
              ? "bg-blue-800 text-white"
              : " text-blue-800 border"
          }`}
        >
          News & Articles
        </button>
        <button
          onClick={() => setTogail("blogs from our experts")}
          className={`py-2 px-5  rounded-md font-semibold ${
            togail === "blogs from our experts"
              ? "bg-blue-800 text-white"
              : " text-blue-800 border"
          }`}
        >
          Blogs From Our Experts
        </button>
      </div>
      <div className="">
        {togail === "success stories" && (
          <div className="flex justify-center flex-wrap  m-auto w-full">
            <div className="swiper-slide swiper-slide-active w-[350px]">
              <div className="success-story p-5 bg-white text-left flex flex-col justify-between">
                <div>
                  <div className="cursor-pointer">
                    <Image
                      alt="Successful Treatment of Rectal Cancer | Patient Success Story"
                      loading="lazy"
                      width={500}
                      height={400}
                      decoding="async"
                      src="https://stgaccinwbsdevlrs01.blob.core.windows.net/newcorporatewbsite/success-stories/February2024/0s79YKYoG3SZPsVmobjR.webp?w=1080&q=75"
                      style={{ color: "transparent" }}
                      className="w-full h-auto"
                    />
                  </div>
                  <h2 className="text-lg font-bold text-gray-800 mt-4 mb-4 cursor-default">
                    Successful Treatment of Rectal Cancer | Patient Success
                    Story
                  </h2>
                  <p
                    id="story-desc-0"
                    className="text-base font-normal text-gray-600 mb-2 cursor-default"
                  >
                    Navigating through the complexities of cancer diagnosis and
                    treatment can be an overwhelming experience, impacting both
                    physical and mental health.
                  </p>
                </div>
                <div>
                  <span className="blogs-card-description-author w-full flex flex-col justify-start items-start pt-4 border-t">
                    {/* Replace with author name or other details if needed */}
                    <span className="text-base font-medium text-gray-800 cursor-default">
                      Cancer Care
                    </span>
                  </span>
                </div>
              </div>
            </div>
            <div className="swiper-slide swiper-slide-active w-[350px]">
              <div className="success-story p-5 bg-white text-left flex flex-col justify-between ">
                <div>
                  <div className="cursor-pointer">
                    <Image
                      alt="Successful Treatment of Rectal Cancer | Patient Success Story"
                      loading="lazy"
                      width={500}
                      height={400}
                      decoding="async"
                      src="https://stgaccinwbsdevlrs01.blob.core.windows.net/newcorporatewbsite/success-stories/February2024/WPJ8q2kocQ0tEBmHRvaT.webp?w=640&q=75"
                      style={{ color: "transparent" }}
                      className="w-full h-auto"
                    />
                  </div>
                  <h2 className="text-lg font-bold text-gray-800 mt-4 mb-4 cursor-default">
                    Successful Treatment of Rectal Cancer | Patient Success
                    Story
                  </h2>
                  <p
                    id="story-desc-0"
                    className="text-base font-normal text-gray-600 mb-2 cursor-default"
                  >
                    Navigating through the complexities of cancer diagnosis and
                    treatment can be an overwhelming experience, impacting both
                    physical and mental health.
                  </p>
                </div>
                <div>
                  <span className="blogs-card-description-author w-full flex flex-col justify-start items-start pt-4 border-t">
                    {/* Replace with author name or other details if needed */}
                    <span className="text-base font-medium text-gray-800 cursor-default">
                      Cancer Care
                    </span>
                  </span>
                </div>
              </div>
            </div>
            <div className="swiper-slide swiper-slide-active w-[350px]">
              <div className="success-story p-5 bg-white text-left flex flex-col justify-between">
                <div>
                  <div className="cursor-pointer">
                    <Image
                      alt="Successful Treatment of Rectal Cancer | Patient Success Story"
                      loading="lazy"
                      width={500}
                      height={400}
                      decoding="async"
                      src="https://stgaccinwbsdevlrs01.blob.core.windows.net/newcorporatewbsite/success-stories/February2024/qX4m5dchJtE6JDiVXYet.webp?w=640&q=75"
                      style={{ color: "transparent" }}
                      className="w-full h-auto"
                    />
                  </div>
                  <h2 className="text-lg font-bold text-gray-800 mt-4 mb-4 cursor-default">
                    Successful Treatment of Rectal Cancer | Patient Success
                    Story
                  </h2>
                  <p
                    id="story-desc-0"
                    className="text-base font-normal text-gray-600 mb-2 cursor-default"
                  >
                    Navigating through the complexities of cancer diagnosis and
                    treatment can be an overwhelming experience, impacting both
                    physical and mental health.
                  </p>
                </div>
                <div>
                  <span className="blogs-card-description-author w-full flex flex-col justify-start items-start pt-4 border-t">
                    {/* Replace with author name or other details if needed */}
                    <span className="text-base font-medium text-gray-800 cursor-default">
                      Cancer Care
                    </span>
                  </span>
                </div>
              </div>
            </div>
            <div className="swiper-slide swiper-slide-active w-[350px]">
              <div className="success-story p-5 bg-white text-left flex flex-col justify-between ">
                <div>
                  <div className="cursor-pointer">
                    <Image
                      alt="Successful Treatment of Rectal Cancer | Patient Success Story"
                      loading="lazy"
                      width={500}
                      height={400}
                      decoding="async"
                      src="https://stgaccinwbsdevlrs01.blob.core.windows.net/newcorporatewbsite/success-stories/February2024/FiQAPsPG2A5n9W7AMCTT.webp?w=640&q=75"
                      style={{ color: "transparent" }}
                      className="w-full h-auto"
                    />
                  </div>
                  <h2 className="text-lg font-bold text-gray-800 mt-4 mb-4 cursor-default">
                    Successful Treatment of Rectal Cancer | Patient Success
                    Story
                  </h2>
                  <p
                    id="story-desc-0"
                    className="text-base font-normal text-gray-600 mb-2 cursor-default"
                  >
                    Navigating through the complexities of cancer diagnosis and
                    treatment can be an overwhelming experience, impacting both
                    physical and mental health.
                  </p>
                </div>
                <div>
                  <span className="blogs-card-description-author w-full flex flex-col justify-start items-start pt-4 border-t">
                    {/* Replace with author name or other details if needed */}
                    <span className="text-base font-medium text-gray-800 cursor-default">
                      Cancer Care
                    </span>
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
        {togail === "news & articles" && (
          <div className="text-center py-4 text-gray-700 font-semibold h-screen">
            Coming Soon
          </div>
        )}
        {togail === "blogs from our experts" && (
          <div className="text-center py-4 text-gray-700 font-semibold h-screen">
            Coming Soon
          </div>
        )}
      </div>
    </div>
  );
};

export default Healthcare;
