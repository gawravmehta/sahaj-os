import Image from "next/image";
import React from "react";

const Audit = () => {
  return (
    <div className="p-6">
      <div className="flex min-h-[calc(100vh-250px)] items-center justify-center">
        <div className="flex flex-col items-center justify-center">
          <div className="w-[200px]">
            <Image
              height={200}
              width={200}
              src="/assets/illustrations/no-data-find.png"
              alt="Circle Image"
              className="h-full w-full object-cover"
            />
          </div>
          <div className="mt-5">
            <p>No Audit Data Available</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Audit;
