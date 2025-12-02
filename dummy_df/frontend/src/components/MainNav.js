"use client";
import { usePathname } from "next/navigation";
import React from "react";
import Navbar2 from "./RealStateComp/Navbar";
import Navbar1 from "./HealthCareComp/Navbar";
import Navbar3 from "./matrimonialComp/NavBar";
import Navbar4 from "./EducationalComp/Navbar"
import Navbar5 from "./bankComps/Navbar";
import Navbar6 from "./megamartComps/Navbar";

const MainNav = () => {
  const pathname = usePathname();

  return (
    <>
      {pathname.includes("/health_care") && <Navbar1 />}
      {pathname.includes("/real_state") && <Navbar2 />}
       {/* {pathname.includes("/matrimonial") && <Navbar3 />} */}
      {pathname.includes("/educational-Institute") && <Navbar4 />}
   

    </>
  );
};

export default MainNav;
