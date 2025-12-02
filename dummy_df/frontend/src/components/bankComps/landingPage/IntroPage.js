import Link from "next/link";
import React from "react";

const IntroPage = () => {
  return (
    <div className="">
      <div
        className="w-full bg-cover bg-no-repeat bg-center pl-28  pt-32 pb-28"
        style={{
          backgroundImage: 'url("./image/salary-ko-jagao-activmoney-d.png")',
        }}
      >
        <div className="">
          <h1 className="text-4xl font-bold text-[#333333] ">
            Salary Ko Jagao
            <br /> ActivMoney mein 7%* p.a.tak
            <br /> kamao!
          </h1>
          <p className="text-[#600000] pt-4 ">
            To know more, <span className="text-[#FF0000]">click here</span>
          </p>
          <div className=" flex gap-1 pt-10">
            <Link href="/trust-bank/register">
              <button className="bg-[#ED4223] text-white rounded-md px-10 py-3 whitespace-nowrap">
                Open a Trust Saving Account
              </button>
            </Link>
            <button className="bg-[#ED4223] text-white rounded-md px-10 py-3 whitespace-nowrap">
              Existing Customer? Activate
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IntroPage;
