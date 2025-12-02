import Footer from "@/components/bankComps/Footer";
import LoanRegister from "@/components/bankComps/LoanRegister";
import Navbar from "@/components/bankComps/Navbar";
import React from "react";

const Page = () => {
  return (
    <div>
      <Navbar />
      <LoanRegister />
      <Footer/>
    </div>
  );
};

export default Page;
