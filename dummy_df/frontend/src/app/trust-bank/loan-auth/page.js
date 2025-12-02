import Footer from "@/components/bankComps/Footer";
import LoanRegister1 from "@/components/bankComps/LoanRegister1";
import Navbar from "@/components/bankComps/Navbar";
import React from "react";

const Page = () => {
  return (
    <div>
      <Navbar />
      <LoanRegister1 />
      <Footer/>
    </div>
  );
};

export default Page;
