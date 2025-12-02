"use client";

import React from "react";
import Footer1 from "./HealthCareComp/Footer";
import Footer2 from "./RealStateComp/Footer";
import { usePathname } from "next/navigation";
import Footer3 from "./matrimonialComp/Footer";
import Footer4 from "./EducationalComp/Footer";

const MainFooter = () => {
  const pathname = usePathname();

  // Condition to not show footer for '/educational-Institute/application-form'
  if (
    pathname === "/educational-Institute/application-form" ||
    pathname === "/educational-Institute/exam-form" ||
    pathname === "/educational-Institute/payment" ||
    pathname === "/educational-Institute/preference-center" ||
    pathname === "/educational-Institute/profile" ||
    pathname === "/real_state/preference-center" ||
    pathname === "/educational-Institute/dashboard"
  ) {
    return null; // Don't render the footer
  }


  return (
    <div>
      {pathname.includes("/health_care") && <Footer1 />}
      {pathname.includes("/real_state") && <Footer2 />}
      {/* {pathname.includes("/matrimonial") && <Footer3 />} */}
      {pathname.includes("/educational-Institute") && <Footer4 />}
    </div>
  );
};

export default MainFooter;
