import React from "react";
import Image from "next/image";

const Recognition = () => {
  return (
    <div className="mt-14">
      <h1 className="text-4xl font-semibold text-black underline text-center decoration-blue-900 decoration-4">
        Approvals and Recognition -{" "}
        <span className="text-[#071C55] underline decoration-blue-900 decoration-4">
          Hogwarts University
        </span>
      </h1>
      <div className="grid grid-cols-5 gap-2 mt-14 mx-10 ">
        <div className="border border-gray-300 h-[350px] hover:border-[#3C4852] shadow-lg rounded-md flex-col justify-center ">
          <div className="p-4">
            <Image
              src="https://www.itmuniversity.org/assets/recognition/ugc.webp"
              alt="University Grant Commission logo"
              width={300} // Adjusted width
              height={200} // Adjusted height
              className="transition-transform duration-250 w-full hover:scale-105"
            />
          </div>
          <h1 className="text-center text-sm  font-bold">
            University Grant Commission
          </h1>
          <p className="text-center text-base ">( UGC )</p>
        </div>

        <div className="border border-gray-300 h-[350px] hover:border-[#3C4852] shadow-lg rounded-md flex-col justify-center items-center ">
          <div className="p-4">
            <Image
              src="https://www.itmuniversity.org/assets/recognition/bci.webp"
              alt="Bar Council of India logo"
              width={300} // Adjusted width
              height={200} // Adjusted height
              className="transition-transform duration-250 w-full hover:scale-105"
            />
          </div>
          <h1 className="text-center text-sm  font-bold">
            Bar Council of India
          </h1>
          <p className="text-center text-base ">( BCI )</p>
        </div>

        <div className="border border-gray-300 h-[350px] hover:border-[#3C4852] shadow-lg rounded-md flex-col justify-center items-center ">
          <div className="p-4">
            <Image
              src="https://www.itmuniversity.org/assets/recognition/coa.webp"
              alt="Council of Architecture logo"
              width={300}
              height={200}
              className="transition-transform w-full duration-250 hover:scale-105"
            />
          </div>
          <h1 className="text-center text-sm  font-bold">
            Council of Architecture
          </h1>
          <p className="text-center text-base ">( COA )</p>
        </div>

        <div className="border h-[350px] border-gray-300 hover:border-[#3C4852] shadow-lg rounded-md flex-col justify-center items-center ">
          <div className="p-4">
            <Image
              src="https://www.itmuniversity.org/assets/recognition/cgpurc.webp"
              alt="Chhattisgarh Private University Regulatory Commission logo"
              width={300}
              height={200}
              className="transition-transform duration-250 w-full hover:scale-105"
            />
          </div>
          <h1 className="text-center text-sm  font-bold">
            Chhattisgarh Private University Regulatory Commission
          </h1>
          <p className="text-center text-base ">( CGPURC )</p>
        </div>

        <div className="border h-[350px] border-gray-300 hover:border-[#3C4852] shadow-lg rounded-md flex-col justify-center items-center ">
          <div className="p-4">
            <Image
              src="https://www.itmuniversity.org/assets/recognition/aiu.webp"
              alt="Member of Association of Indian Universities logo"
              width={300}
              height={200}
              className="transition-transform duration-250 w-full hover:scale-105"
            />
          </div>
          <h1 className="text-center text-sm  font-bold">
            Member of Association of Indian Universities
          </h1>
          <p className="text-center text-base ">( AIU )</p>
        </div>
      </div>
    </div>
  );
};

export default Recognition;
