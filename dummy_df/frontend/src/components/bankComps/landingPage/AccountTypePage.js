import Image from "next/image";
import React from "react";
import { IoIosArrowDropright } from "react-icons/io";

const AccountTypePage = () => {
  return (
    <div className="flex justify-center items-center px-28 py-14 bg-[#ECECED] gap-8">
      <div className="max-w-sm bg-white border border-gray-200 rounded-md shadow ">
        <Image
          height={200}
          width={200}
          className="rounded-md object-fill w-full"
          src="https://www.kotak.com/content/dam/Kotak/herosliderbanner/WebSite-1099-295x165.jpg.transform/transformer-width-360-height-202/image.jpg"
          alt="pic"
        />

        <div className="p-5">
          <h1 className="font-semibold text-sm">LOANS</h1>

          <h5 className="mt-5 text-2xl font-base tracking-tight text-gray-700 dark:text-white">
            Personal Loan at incredibly low rates
          </h5>

          <p className="mt-3 font-normal  text-gray-700 ">
            Quick loan saction | Part Prepayment available| Loan amount up to
            Rs.40 lakh
          </p>
          <button className="inline-flex gap-2 items-center  py-2 text-sm font-semibold text-center text-[#FF1800] ">
            Apply Now
            <IoIosArrowDropright className="h-5 w-5" />
          </button>
        </div>
      </div>
      <div className="max-w-sm bg-white border border-gray-200 rounded-lg shadow ">
        <a href="#">
          <Image
            height={200}
            width={200}
            className="rounded-t-lg object-fill w-full"
            src="https://www.kotak.com/content/dam/Kotak/Product-Card-Images-Mobile/reliance-digital-offer.jpg.transform/transformer-width-360-height-202/image.jpg"
            alt="pic"
          />
        </a>
        <div className="p-5">
          <h1 className="font-semibold text-sm">SAVING ACCOUNT</h1>

          <h5 className="mt-5 text-2xl font-base tracking-tight text-gray-700 ">
            Personal Loan at incredibly low rates
          </h5>

          <p className="mt-3 font-normal  text-gray-700 ">
            Quick loan saction | Part Prepayment available| Loan amount up to
            Rs.40 lakh
          </p>
          <button className="inline-flex gap-2 items-center py-2 text-sm font-medium text-center text-[#FF1800] rounded-lg  focus:ring-4 focus:outline-none ">
            Apply Now
            <IoIosArrowDropright className="h-5 w-5" />
          </button>
        </div>
      </div>
      <div className="max-w-sm bg-white border border-gray-200 rounded-lg shadow ">
        <Image
          height={200}
          width={200}
          className="rounded-t-lg object-fill w-full"
          src="https://www.kotak.com/content/dam/Kotak/product_card_images/CBDC-product-t.jpg.transform/transformer-width-360-height-202/image.jpg"
          alt="pic"
        />

        <div className="p-5">
          <h1 className="font-semibold text-sm">CURRENT ACCOUNT</h1>

          <h5 className="mt-5 text-2xl font-base tracking-tight text-gray-700 ">
            Personal Loan at incredibly low rates
          </h5>

          <p className="mt-3 font-normal  text-gray-700 ">
            Quick loan saction | Part Prepayment available| Loan amount up to
            Rs.40 lakh
          </p>
          <button className="inline-flex gap-2 items-center py-2 text-sm font-medium text-center text-[#FF1800]">
            Know More
            <IoIosArrowDropright className="h-5 w-5" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default AccountTypePage;
