import Button from "@/components/ui/Button";
import React from "react";
import { FaCheckCircle } from "react-icons/fa";
import { IoMdArrowBack } from "react-icons/io";
import Link from "next/link";

const UploadSucessfully = ({ dpLength, pathname }) => {
  return (
    <div className="flex">
      <div className="flex flex-col items-center justify-center p-10">
        <FaCheckCircle className="h-20 w-20 text-[#17C935]" />

        <h1 className="text-[22px] mt-3 ">
          {dpLength} Data Principal Added Successfully
        </h1>
        <p className="pb-3 pt-1 text-xs text-[#8A8A8A]">
          You will be notified once the Data Principals are created.
        </p>
        {pathname.startsWith(
          "/user/principal-management/persona-management/add-bulk-dp/"
        ) ? (
          <Link href="/user/principal-management/persona-management">
            <Button variant="primary" className="mt-2 w-52 gap-2 text-nowrap">
              <IoMdArrowBack className="" />
              Back to Persona Management
            </Button>
          </Link>
        ) : (
          <Link href="/apps/principal-management">
            <Button variant="primary" className="mt-2 w-52 gap-2 text-nowrap">
              <IoMdArrowBack className="" />
              Back to Data Principal
            </Button>
          </Link>
        )}
      </div>
    </div>
  );
};

export default UploadSucessfully;
