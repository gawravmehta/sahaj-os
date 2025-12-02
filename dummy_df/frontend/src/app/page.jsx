import React from "react";

import Stories from "@/components/bankComps/landingPage/Stories";

import IntroPage from "@/components/bankComps/landingPage/IntroPage";
import AccountTypePage from "@/components/bankComps/landingPage/AccountTypePage";
import PaymentTypePage from "@/components/bankComps/landingPage/PaymentTypePage";
import Navbar from "@/components/bankComps/Navbar";
import Footer from "@/components/bankComps/Footer";

const Page = () => {
  return (
    <div>
      <Navbar />
      <IntroPage />
      <AccountTypePage />
      <Stories />
      <PaymentTypePage />
      <Footer />
    </div>
  );
};

export default Page;
