import Footer from "@/components/bankComps/Footer";
import LoanForm1 from "@/components/bankComps/form/LoanForm1";
import Navbar from "@/components/bankComps/Navbar";
import React from "react";

const Page = () => {
  return (
    <div>
      <Navbar />
     
      <LoanForm1 />
      <Footer/>
    </div>
  );
};

export default Page;
