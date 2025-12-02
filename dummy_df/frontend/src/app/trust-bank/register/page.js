"use client";

import Footer from "@/components/bankComps/Footer";
import Navbar from "@/components/bankComps/Navbar";
import RegisterForm1 from "@/components/bankComps/form/RegisterForm1";
import React, { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

// Function for showing notice, modified to handle dynamic import
const handleShowNotice = async (router, setDisabled1) => {
  if (typeof window !== "undefined") {
    const { morajNoticeCenter } = await import(
      "concur-consent/morajNoticeCenter"
    );

    console.log("handleShowNotice function call");
    const agreementId = localStorage.getItem("agreement_id");
    if (agreementId) {
      // If agreement_id exists, route to the landing page
      router.push("/trust-bank/home"); // Replace with your actual landing page route
      localStorage.removeItem("agreement_id");
    } else {
      // If agreement_id doesn't exist, show the notice center
      morajNoticeCenter(
        "66c7099f8039b28a25d760e6",
        "bebdbc7d6478da15",
        "66c7080d8039b28a25d760e4",
        "UBgPUCMdp8iXV4ZZ7Ks7DA",
        "-_TF41WvWHwwYfV28IUi1aH503T8GXxIWvj2s6MKda0"
      );
      setTimeout(() => {
        setDisabled1(false);
      }, 2000);
    }
  }
};

const Page = () => {
  const router = useRouter();
  const [disabled1, setDisabled1] = useState(false);
  const [formData, setFormData] = useState({
    fullName: "",
    email: "",
    phoneNumber: "",
    dob: "",
    address: "",
  });

  const updateFormData = () => {
    setFormData({
      fullName: "Gaurav Mehta",
      email: "gewgawrav@gmail.com",
      phoneNumber: "8770467824",
      dob: "1947-02-28", // Valid date in 'YYYY-MM-DD' format
      address: "Raipur. Chhattishgarh",
    });
  };

  return (
    <div className="flex flex-col">
      <Navbar />
      <div className="flex justify-center items-center mt-10 mb-20">
        <button
          onClick={updateFormData}
          className=" absolute top-24 right-10 text-red-500 border border-red-500 focus:ring-4 hover:bg-red-500 hover:text-white font-medium rounded-md text-base w-full sm:w-auto px-7 py-3 text-center"
        >
          Fill Data
        </button>
        <div className="flex flex-col items-center w-1/2 hover:shadow-2xl mb-5 justify-center p-8">
          <h1 className="text-3xl w-full text-center text-[#003366]">
            Please leave your details and we will get in touch with you
          </h1>
          <hr className="mt-5 w-full h-0.5 bg-gray-300" />
          <RegisterForm1
            setDisabled1={setDisabled1}
            disabled1={disabled1}
            className=""
            formData={formData} // Pass setDisabled1 here
            setFormData={setFormData} // Pass setDisabled1 here
          />
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default Page;
