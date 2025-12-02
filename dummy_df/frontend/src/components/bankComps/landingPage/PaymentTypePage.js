import Image from "next/image";
import React from "react";
import { IoIosArrowDropright } from "react-icons/io";
import { IoIosArrowDropdown } from "react-icons/io";
import { IoIosArrowDropup } from "react-icons/io";
const PaymentTypePage = () => {
  return (
    <div className="flex flex-col  px-28 py-10 bg-[#ECECED] gap-7">
      <div className="flex gap-7">
        <div className="bg-white rounded-lg  w-[30vw]">
          <Image
            width={200}
            height={200}
            className="rounded-t-lg object-fill w-full"
            src="https://www.kotak.com/content/dam/Kotak/Product-Card-Images-Mobile/bhim-upi-banner.jpg.transform/transformer-width-360-height-202/image.jpg"
            alt="pic"
          />

          <div className="p-8">
            <h1 className="text-3xl">BHIM UPI</h1>

            <h5 className="mb-2 pt-10 text-sm font-normal tracking-tight text-gray-900 ">
              Instant & secure money transfer 24/7 without entering bank
              details.
            </h5>

            <button className="inline-flex pt-20 gap-2 items-center px-1 py-2 text-sm font-semibold text-center text-[#FF1800] ">
              Know More
              <IoIosArrowDropright className="h-5 w-5" />
            </button>
          </div>
        </div>

        <div className=" bg-white rounded-lg w-[30vw]">
          <Image
            width={200}
            height={200}
            className="rounded-t-lg object-fill w-full"
            src="https://www.kotak.com/content/dam/Kotak/product_card_images/mb-app-new-t.jpg.transform/transformer-width-360-height-202/image.jpg"
            alt="pic"
          />

          <div className="p-5">
            <h1 className="text-sm font-medium">WAYS TO BANK</h1>

            <h5 className="mb-2 pt-5 text-2xl font-base tracking-tight text-gray-900 ">
              Did you know? One app can do it all!
            </h5>

            <p className="mb-3 pt-3 font-normal text-gray-700 ">
              Bank,invest,shop,travel,pay & more with the Lena Mobile Banking
              App!
            </p>
            <button className="inline-flex pt-6 gap-2 items-center px-3 py-2 text-sm font-semibold text-center text-[#FF1800] rounded-lg  focus:ring-4 focus:outline-none ">
              Know More
              <IoIosArrowDropright className="h-5 w-5" />
            </button>
          </div>
        </div>

        <div className=" bg-white rounded-lg w-[30vw]">
          <Image
            width={200}
            height={200}
            className="rounded-t-lg object-fill w-full "
            src="https://www.kotak.com/content/dam/Kotak/Product-Card-Images-Mobile/ckyc-t.jpg.transform/transformer-width-360-height-202/image.jpg"
            alt="pic"
          />

          <div className="p-5">
            <h5 className="mb-2 text-3xl font-base tracking-tight text-[#333333] ">
              Ask for your CKYC Identifier today!
            </h5>

            <p className=" pt-5 font-normal text-sm text-gray-700 ">
              Benefits of the identifire: Linked to your KYC data | Open A/c
              faster with reduced paperwork | No repeated submission of
              documents
            </p>
            <button className="inline-flex gap-2 items-center pt-12 text-sm font-semibold text-center text-[#FF1800]">
              Know More
              <IoIosArrowDropright className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
      <div className="flex gap-7">
        <div className="bg-white rounded-lg w-[30vw]">
          <Image
            width={200}
            height={200}
            className="rounded-t-lg object-fill w-full"
            src="https://www.kotak.com/content/dam/Kotak/deals-offers/shopping/itc-offer-t.jpg"
            alt="pic"
          />

          <div className="p-8">
            <h1 className="text-xl">ITCSTORE</h1>

            <h5 className="mb-2 pt-10 text-sm font-normal tracking-tight text-gray-900 ">
              Upto 45% OFF + EXTRA Rs.200 OFF on ITC Store!
            </h5>
            <p>Valid till: 30 September 2024</p>

            <button className="inline-flex pt-20 gap-2 items-center px-1 py-2 text-sm font-semibold text-center text-[#FF1800] ">
              Know More
              <IoIosArrowDropright className="h-5 w-5" />
            </button>
          </div>
        </div>

        <div className=" bg-white rounded-lg w-[30vw]">
          <Image
            width={200}
            height={200}
            className="rounded-t-lg object-fill w-full"
            src="https://www.kotak.com/content/dam/Kotak/feature-cards/Channel-Red.jpg.transform/transformer-width-360-height-202/image.jpg"
            alt="pic"
          />

          <div className="p-5">
            <h1 className="text-2xl">Tune in to Channel Red</h1>

            <p className="mb-3 pt-3 font-normal text-gray-700 dark:text-gray-400">
              Explore a treasure trove of information about our products and
              services on Digital Platforms.
            </p>
            <button className="inline-flex pt-24 gap-2 items-center px-3 py-2 text-sm font-semibold text-center text-[#FF1800] rounded-lg  focus:ring-4 focus:outline-none ">
              Know More
              <IoIosArrowDropright className="h-5 w-5" />
            </button>
          </div>
        </div>

        <div className=" bg-white rounded-lg w-[30vw]">
          <div className="bg-[#666666] w-full h-16 rounded-t-md p-5">
            <h1 className="text-white text-2xl">Rates & Charges</h1>
          </div>
          <div className="px-10">
            <div className="flex items-center justify-between pt-4 ">
              <div className="flex items-center gap-1">
                <Image
                  width={200}
                  height={200}
                  className="w-[70px] h-10 rounded-md"
                  src="https://www.kotak.com/content/dam/Kotak/svg-icons/icon-piggy-bank.svg"
                  alt="Neil image"
                />
                <p className="text-[14px] font-medium text-gray-700 ">
                  Deposits
                </p>
              </div>

              <div className="inline-flex items-center text-lg font-semibold text-[#EE1C25]">
                <IoIosArrowDropup className="h-5 w-5" />
              </div>
            </div>

            <h1 className=" pt-5 font-medium">
              Fixed Deposite(12 months 25 days)
            </h1>

            <div className="flex items-center justify-between ">
              <div className="flex-shrink-0">
                <h1 className="text-[#EE1C25]">Regular </h1>
              </div>

              <div className="inline-flex items-center text-md font-medium ">
                7.40%
              </div>
            </div>
            <div className="flex items-center text-md font-medium justify-between ">
              <div className="flex-shrink-0">
                <h1 className="text-[#EE1C25]">Senior Citizen </h1>
              </div>

              <div className="inline-flex items-center text-md font-medium">
                7.9%
              </div>
            </div>

            <div className="flex items-center mt-4 justify-between border-t  border-gray-100 py-4 ">
              <div className="flex items-center gap-2 ">
                <Image
                  width={50}
                  height={50}
                  className=" h-10 rounded-md"
                  src="https://www.kotak.com/content/dam/Kotak/svg-icons/icon-money-wallet.svg"
                  alt="Neil image"
                />
                <p className="text-[14px] font-light text-[#828282]">
                  Saving Account
                </p>
              </div>

              <div className="inline-flex items-center text-lg font-semibold text-[#EE1C25]">
                <IoIosArrowDropdown className="h-5 w-5" />
              </div>
            </div>

            <div className="flex items-center  justify-between border-t border-gray-100  py-4">
              <div className="flex items-center gap-2">
                <Image
                  width={50}
                  height={50}
                  className=" h-10 rounded-md"
                  src="https://www.kotak.com/content/dam/Kotak/svg-icons/rate-loans.svg"
                  alt="Neil image"
                />
                <p className="text-[14px] font-light text-[#828282]  text-wrap">
                  Loans
                </p>
              </div>

              <div className="inline-flex items-center text-lg font-semibold text-[#EE1C25]">
                <IoIosArrowDropdown className="h-5 w-5" />
              </div>
            </div>

            <button className="inline-flex gap-2 items-center pt-20 text-sm font-semibold text-center text-[#FF1800]">
              See all rates
              <IoIosArrowDropright className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PaymentTypePage;
