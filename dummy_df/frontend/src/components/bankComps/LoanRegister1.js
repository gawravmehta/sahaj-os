"use client";

import React, { useState } from "react";
import CaptchaGenerator from "./CaptchaGenerator";
import Link from "next/link";
import Image from "next/image";
import { IoMdRefresh } from "react-icons/io";

const LoanRegister1 = () => {
 
  const [formData, setFormData] = useState({
    contact: "",
    userInput:"",
    dob: "",
    crn: "",

  });


 const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevFormData) => ({
      ...prevFormData,
      [name]: value,
    }));
  };

  const updateFormData = () => {
    setFormData({
      contact: "123-456-7890", // Example contact number
      dob: "1990-01-01",      // Example date of birth
      crn: "CRN123456", 
      userInput:" jSy4N7"      // Example CRN
    });
  };

  
  return (
    <div className="mt-3 flex justify-center items-center mb-20">
      <div className="w-[70%] shadow-md pb-5 rounded-sm">
        <div className="w-full  bg-[#EEEEEE]">
          <h1 className="text-center text-red-600 font-medium text-xl w-ful py-2">
            Authentication
          </h1>{" "}
          <div className="flex w-full justify-between gap-5 px-2 mt-5">
            <div className=" w-1/3 p-2">
              <div className="border-[1.8px] text-red-600 font-medium border-dashed border-[#b8dae8] rounded-full h-10 w-10 items-center justify-center flex">
                1
              </div>
              <div className="flex flex-col text-blue-900 w-full justify-center items-center ">
                <Image
                  src="/image/Authenticate.png"
                  alt="Authenticate.png"
                  height={190}
                  width={190}
                />
                <p>Authenticate</p>
              </div>
            </div>
            <div className=" w-1/3 p-2">
              <div className="border-[1.8px] text-red-600 font-medium border-dashed border-[#b8dae8] rounded-full h-10 w-10 items-center justify-center flex">
                2
              </div>
              <div className="flex w-full flex-col text-blue-900 justify-center items-center ">
                <Image
                  src="/image/Success.png"
                  alt="Success.png"
                  height={163}
                  width={163}
                />
                <p className="mt-3">Fill Application Form</p>
              </div>
            </div>
            <div className=" w-1/3 p-2">
              <div className="border-[1.8px] text-red-600 font-medium border-dashed border-[#b8dae8] rounded-full h-10 w-10 items-center justify-center flex">
                3
              </div>
              <div className="flex w-full flex-col text-blue-900 justify-center items-center ">
                <Image
                  src="/image/Fill_Application_Form.png"
                  alt="Authenticate.png"
                  height={185}
                  width={185}
                />
                <p>Success </p>
              </div>
            </div>
          </div>
        </div>
        <div className="flex flex-col w-full justify-center items-center mt-5">
          <h4 className="text-center font-medium">
            Please enter the following details to get started
          </h4>
          <div className="w-full px-3 mt-5">
            <div className="flex w-full justify-between ">
              <div className="flex flex-col w-full">
                <label className="text-gray-400" for="">
                  Registered Mobile Number
                </label>
                <input
                  type="text"
                  value={formData.contact}
            onChange={handleChange}
                  className="w-1/2 border-b border-gray-300 focus:outline-none focus:ring-blue-300 focus:border-blue-300"
                  maxLength={10}
                  onInput={(e) => {
                    const onlyNum = e.target.value.replace(/[^0-9]/g, "");
                    setContact(onlyNum);
                  }}
                />
              </div>

              <button
                onClick={updateFormData}
                className="   text-red-500 border border-red-500 focus:ring-4 hover:bg-red-500 hover:text-white font-medium rounded-md text-base  w-24 text-center"
              >
                Fill Data
              </button>
            </div>

            <div className=" flex  justify-between mt-10 w-full items-center my-10">
              <div className="flex flex-col mt-3 w-1/2">
                <label className="text-gray-400" for="">
                  Data Of Birth
                </label>
                <input
                  type="date"
                  value={formData.dob}
                  onChange={handleChange}
                  className="w-[70%]  border-b border-gray-300 focus:outline-none focus:ring-blue-300 focus:border-blue-300 placeholder:-text-gray-300"
                />{" "}
              </div>
              <span className="-mb-10">OR</span>
              <div className="flex flex-col mt-4 w-1/2 pl-20  ">
                <label className="text-gray-400" for="">
                  CRN
                </label>
                <input
                  type="text"
                  value={formData.crn}
                  onChange={handleChange}
                  className="w-[100%] border-b border-gray-300 focus:outline-none focus:ring-blue-300 focus:border-blue-300"
                  maxLength={10}
                />
              </div>
            </div>
            <div>
            <div className="mt-12">
      <p className="text-gray-300 text-lg font-semibold">
        Type the code shown (Case Sensitive)
      </p>
      <div className="captcha-box flex items-center gap-2 mb-4 ">
        <span className="text-lg font-bold tracking-widest w-16">
          
          jSy4N7
        </span>
        <button  className="ml-2">
          <IoMdRefresh size={20} />
        </button>
        <input
          type="text"
          placeholder="Enter Code"
          value={formData.userInput}
          onChange={handleChange}
          // onChange={(e) => setUserInput(e.target.value)}
          className="w-1/4 py-2 border-b border-gray-300 outline-none mb-4"
        />
      </div>
    </div>
            </div>
            <div className="flex justify-center items-center mt-5">
              <Link href="/trust-bank/home-loan">
                <button className="bg-red-500 text-white px-10 py-2 rounded-sm">
                  Next
                </button>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoanRegister1;
