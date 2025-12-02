import Footer from "@/components/bankComps/Footer";
import Navbar from "@/components/bankComps/Navbar";
import RegisterForm from "@/components/bankComps/form/RegisterForm";
import React from "react";

const Page = () => {
  return (
    <div className=" flex flex-col ">
      <Navbar />
      <div className="flex justify-center items-center mt-10 mb-20 ">
        <div className="flex flex-col items-center w-1/2 hover:shadow-2xl mb-5 justify-center  p-8">
          <h1 className="text-3xl w-full text-center text-[#003366]">
            Please leave your details and we will get in touch with you
          </h1>
          <hr className="mt-5 w-full h-0.5 bg-gray-300" />

          <RegisterForm className="" />
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default Page;
