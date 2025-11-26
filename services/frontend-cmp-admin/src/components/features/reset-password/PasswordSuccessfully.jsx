"use client";

import Image from "next/image";
import Link from "next/link";
import { IoIosCheckmarkCircle } from "react-icons/io";
import { HiArrowNarrowRight } from "react-icons/hi";
import Loader from "@/components/ui/Loader";

const PasswordSuccessfully = ({
  title,
  desc,
  button,
  path,
  loading,
  arrowLeft = false,
}) => {
  if (loading) {
    return <Loader />;
  }
  return (
    <div className="flex min-h-screen flex-col items-center bg-[url('/bg-images/Bg-48-percent-opacity.png')] bg-cover bg-center px-5 py-20 sm:justify-center sm:py-10">
      <div className="mb-8">
        <Image
          src="/assets/sahaj-logos/sahaj.png"
          alt="logo"
          width={150}
          height={150}
          className="h-9 w-40 object-contain"
        />
      </div>
      <div className="h-[330px] w-[420px] bg-background p-6 shadow-[0_4px_16px_rgba(0,47,167,0.1)]">
        <IoIosCheckmarkCircle
          size={60}
          className="mx-auto mb-5 text-[#06A42A]"
        />
        <div className="flex flex-col items-center justify-center">
          <h1 className="text-[24px] text-heading"> {title}</h1>
          <p className="text-subText mt-1 text-sm">{desc}</p>
        </div>

        <div className="mt-6 flex justify-center sm:mt-8">
          <Link
            href={path}
            className="m-auto flex h-10 w-full items-center justify-center gap-2 border bg-primary text-center text-white"
          >
            {arrowLeft && (
              <HiArrowNarrowRight size={17} className="-mb-0.5 rotate-180" />
            )}
            <span className="text-sm">{button}</span>
            {!arrowLeft && (
              <HiArrowNarrowRight size={17} className="-mb-0.5" />
            )}
          </Link>
        </div>
      </div>
    </div>
  );
};

export default PasswordSuccessfully;
