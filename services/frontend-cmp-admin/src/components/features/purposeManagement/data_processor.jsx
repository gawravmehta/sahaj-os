import Image from "next/image";
import React from "react";

const data_processor = () => {
  return (
    <div className="flex min-h-[calc(100vh-250px)] items-center justify-center">
      <div className="flex flex-col items-center justify-center">
        <div className="w-52">
          <Image
            height={200}
            width={200}
            src="/assets/illustrations/no-data-find.png"
            alt="Circle Image"
            className="h-full w-full object-cover"
          />
        </div>
        <div>
          <p className="mt-2 text-subText"> No Data Processor available</p>
        </div>
      </div>
    </div>
  );
};

export default data_processor;
