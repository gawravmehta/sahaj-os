"use client";
import React, { useState } from "react";
import RegisterForm from "../FormComponent/RegisterForm";
import { useRouter } from "next/navigation";

const IntroPage = () => {
  const router = useRouter();
  const [disabled, setDisabled] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    mobile: "",
    state: "",
    city: "",
    level: "",
    stream: "",
    program: "",
  });

  const handleApplyClick = () => {
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
  };

  const handleShowNotice = async () => {
    setDisabled(true);
    if (typeof window !== "undefined") {
      const { morajNoticeCenter } = await import(
        "concur-consent/morajNoticeCenter"
      );

      console.log("handleShowNotice function call");
      const agreementId = localStorage.getItem("agreement_id");
      if (agreementId) {
        router.push("/educational-Institute/dashboard");
        localStorage.removeItem("agreement_id");
      } else {
        morajNoticeCenter(
          "66d5a5b3cbd66ef0ea3627e7",
          "33a63dcfcc9a1e8d",
          "66d5a0fdcbd66ef0ea3627e5",
          "fweWzJHL0aaFZpHx9MWI3Q",
          "0zIgEDdg3WbyU2Ev-6vpUz1oa3CUh9yHereJzAVtVsA"
        );
        setTimeout(() => {
          setDisabled(false);
        }, 2000);
      }
    }
  };

  const updateFormData = () => {
    setFormData({
      name: "John Doe",
      email: "john.doe@example.com",
      mobile: "9876543210",
      state: "California",
      city: "Los Angeles",
      level: "Graduate",
      stream: "Science",
      program: "B.Sc",
    });
  };

  return (
    <div
      className="h-[90vh] w-full bg-cover justify-between px-10 flex  mt-28 bg-[#5470bd]"
      style={{
        backgroundImage:
          'url("https://admission.matsuniversity.ac.in/wp-content/uploads/2024/02/MATS_02-1-scaled.jpg")',
      }}
    >
      <div className="w-[30vw] flex pt-20  pl-16">
        <div>
          <h1 className="text-5xl font-bold text-white">
            Experiential Learning
          </h1>
          <h1 className="text-4xl text-white font-bold mt-2">at its best!</h1>
          <p className="text-white mt-5">
            Pursue your Passion with{" "}
            <span className="text-white font-semibold text-lg">
              Hogwarts University
            </span>
          </p>
          <div className="flex gap-5 mt-10">
            <button
              className="bg-[#3C4852] rounded-md text-white px-4 py-3"
              onClick={handleApplyClick}
            >
              Admission Open For 2024-25
            </button>
            <button
              className="bg-[#3C4852] rounded-md text-white py-3 px-3"
              onClick={handleApplyClick}
            >
              Enquire Now
            </button>
          </div>
        </div>
      </div>

      <div className="w-[35vw] p-4  pt-20 flex gap-10">
        <RegisterForm
          handleShowNotice={handleShowNotice}
          setDisabled={setDisabled}
          disabled={disabled}
          formData={formData}
          setFormData={setFormData}
        />
        <button
          onClick={updateFormData}
          className="bg-white h-14 w-32 text-[#071C55] border border-[#071C55] focus:ring-2 hover:bg-[#071C55] hover:text-white font-medium rounded-md text-sm    py-1 text-center"
        >
          Fill data
        </button>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white rounded-lg shadow-xl flex justify-end p-2 w-[100%] max-w-md">
            <button
              onClick={handleCloseModal}
              className="absolute z-40 text-xl pr-2 text-white"
            >
              x
            </button>
            <RegisterForm
              handleShowNotice={handleShowNotice}
              setDisabled={setDisabled}
              disabled={disabled}
              formData={formData}
              setFormData={setFormData}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default IntroPage;
