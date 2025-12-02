import Image from "next/image";
import React from "react";
import { IoIosArrowForward } from "react-icons/io";
import { IoIosArrowDropright } from "react-icons/io";

const Stories = () => {
  return (
    <div className="px-28 flex items-center justify-center bg-[#ECECED] gap-10">
      <div
        className=" h-[80vh] w-[68%] bg-cover flex items-end   rounded-lg"
        style={{
          backgroundImage:
            'url("https://www.kotak.com/content/dam/Kotak/article-images/who-is-a-co-applicant-and-the-benefits-to-co-applicant-for-home-loan-article.jpg.transform/transformerWidth750Height460/image.jpg")',
        }}
      >
        <div className="flex bg-black bg-opacity-40 flex-col  w-full rounded-lg h-28 ">
          <div className="flex flex-col justify-between p-4 leading-normal ">
            <h1 className="text-white">Stories in foucs</h1>
            <h5 className="pt-4 text-xl font-semibold tracking-tight text-white">
              Noteworthy technology acquisitions 2021
            </h5>
            <button className="inline-flex gap-2 items-center  py-2 text-sm font-semibold text-center text-white ">
              Read More
              <IoIosArrowDropright className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
      <div className="w-[33%] ">
        <div className="w-full max-w-md p-4 pb-2 bg-white border border-gray-200 rounded-lg ">
          <div className="flex items-center justify-between ">
            <h5 className="text-xl font-bold leading-none text-gray-900 dark:text-white">
              Stories in focus
            </h5>
          </div>
          <div className="">
            <ul
              role="list"
              className="divide-y divide-gray-200 dark:divide-gray-700"
            >
              <li className="py-3">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Image
                      width={70}
                      height={10}
                      className="w-[70px] h-10 rounded-md"
                      src="https://www.kotak.com/content/dam/Kotak/Product-Card-Images-Mobile/Product-Card-mobile-sweep-facility.jpg"
                      alt="Neil image"
                    />
                  </div>
                  <div className="flex-1 min-w-0 ms-4">
                    <p className="text-[14px] font-light text-[#828282]  text-wrap">
                      Understanding auto sweep facility for saving account
                    </p>
                  </div>
                  <div className="inline-flex items-center text-lg font-semibold text-[#EE1C25]">
                    <IoIosArrowForward />
                  </div>
                </div>
              </li>
              <li className="py-3">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Image
                      width={70}
                      height={10}
                      className="w-[70px] h-10 rounded-md"
                      src="https://www.kotak.com/content/dam/Kotak/Product-Card-Images-Mobile/how-to-pay-advance-tax-online-in-simple-steps-t.jpg"
                      alt="Neil image"
                    />
                  </div>
                  <div className="flex-1 min-w-0 ms-4">
                    <p className="text-[14px] font-light text-[#828282]  text-wrap">
                      How to Pay Advance Tax Online in Simple Steps
                    </p>
                  </div>
                  <div className="inline-flex items-center text-lg font-semibold text-[#EE1C25]">
                    <IoIosArrowForward />
                  </div>
                </div>
              </li>
              <li className="py-3 ">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Image
                      width={70}
                      height={10}
                      className="w-[70px] h-10 rounded-md"
                      src="https://www.kotak.com/content/dam/Kotak/article-images/product-card/Website-358-x-201-7a.jpg"
                      alt="Neil image"
                    />
                  </div>
                  <div className="flex-1 min-w-0 ms-4">
                    <p className="text-[14px] font-light text-[#828282]  text-wrap">
                      10 Best Laptop Brands in India (2024): Buy with Credit
                      Card No Cost EMI
                    </p>
                  </div>
                  <div className="inline-flex items-center text-lg font-semibold text-[#EE1C25]">
                    <IoIosArrowForward />
                  </div>
                </div>
              </li>
              <li className="py-3 ">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Image
                      width={70}
                      height={10}
                      className="w-[70px] h-10 rounded-md"
                      src="https://www.kotak.com/content/dam/Kotak/article-images/house-rent-allowance-hra-358-x-201.jpg"
                      alt="Neil image"
                    />
                  </div>
                  <div className="flex-1 min-w-0 ms-4 ">
                    <p className="text-[14px] font-light text-[#828282]  ">
                      HRA (House Rent Allowence ):
                      <br /> Full Form,Calculate,Example,
                      <br />
                      Meaning,Formula & Receipt Format
                    </p>
                  </div>
                  <div className="inline-flex items-center text-lg font-semibold text-[#EE1C25]">
                    <IoIosArrowForward />
                  </div>
                </div>
              </li>
              <li className="py-3 ">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Image
                      width={70}
                      height={10}
                      className="w-[70px] h-10 rounded-md"
                      src="https://www.kotak.com/content/dam/Kotak/article-images/indiramma-indlu-housing-scheme-358-x-201.jpg"
                      alt="Neil image"
                    />
                  </div>
                  <div className="flex-1 min-w-0 ms-4">
                    <p className="text-[14px] font-light text-[#828282]  text-wrap">
                      Telangana Indiramma Indlu
                      <br /> Housing Scheme-Benefits,
                      <br />
                      Application Form & Eligibility & Allotments
                    </p>
                  </div>
                  <div className="inline-flex items-center text-lg font-semibold text-[#EE1C25]">
                    <IoIosArrowForward />
                  </div>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Stories;
