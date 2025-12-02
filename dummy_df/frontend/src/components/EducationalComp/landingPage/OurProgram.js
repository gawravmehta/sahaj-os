import React from "react";
import { CgProfile } from "react-icons/cg";

const OurProgram = () => {
  return (
    <div className="mt-16">
      <div className="text-center">
        <h1 className="text-4xl underline text-black font-bold decoration-blue-900 decoration-4">
          Our Programs
        </h1>
      </div>
      <div className="flex justify-center gap-5 mt-16">
        <div className="max-w-xs bg-white  rounded-lg shadow-2xl">
          <div className=" flex justify-center items-center p-2">
            <CgProfile
              style={{ width: "100px", height: "100px" }}
              className="fill-slate-500"
            />
          </div>

          <div className="p-5 bg-[#071C55]">
            <h5 className="mb-2 text-lg font-medium text-center text-white">
              UNDER GRADUATION
            </h5>

            <p className="mb-3 font-light text-sm text-white text-center mt-5">
              BBA, B.Tech, B.Sc.(Hons) Microbiology , BCA, B.Com.(Hons), BBA
              LL.B, BAIHTM (Hons), B. Arch.
            </p>
            <button className="items-center mt-5 w-full px-3 py-2 text-lg font-medium text-center text-gray-800 bg-white rounded-lg ">
              Explore more
            </button>
          </div>
        </div>
        <div className="max-w-xs bg-white  rounded-lg shadow-2xl">
          <div className=" flex justify-center items-center p-2">
            <CgProfile
              style={{ width: "100px", height: "100px" }}
              className="fill-slate-500"
            />
          </div>

          <div className="p-5 bg-[#071C55]">
            <h5 className="mb-2 text-lg font-medium text-center text-white">
              POST GRADUATION
            </h5>

            <p className="mb-3 font-light text-sm text-white text-center mt-5">
              MBA Dual Specialization,M.Com,M.C.A.,M.Sc Microbiology, LLM
            </p>
            <button className="items-center mt-5 w-full px-3 py-2 text-lg font-medium text-center text-gray-800 bg-white rounded-lg ">
              Explore more
            </button>
          </div>
        </div>
        <div className="max-w-xs bg-white  rounded-lg shadow-2xl">
          <div className=" flex justify-center items-center p-2">
            <CgProfile
              style={{ width: "100px", height: "100px" }}
              className="fill-slate-500"
            />
          </div>

          <div className="p-5 bg-[#071C55]">
            <h5 className="mb-2 text-lg font-medium text-center text-white">
              Ph.D.
            </h5>

            <p className="mb-3 font-light text-sm text-white text-center mt-5">
              MBA Dual Specialization,M.Com,M.C.A.,M.Sc Microbiology, LL
            </p>
            <button className="items-center mt-5 w-full px-3 py-2 text-lg font-medium text-center text-gray-800 bg-white rounded-lg ">
              Explore more
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OurProgram;
