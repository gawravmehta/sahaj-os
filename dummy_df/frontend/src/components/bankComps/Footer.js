"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

const Footer = () => {
  const router = useRouter();
  const removeLocalStorage = () => {
    localStorage.clear();
    router.push("/trust-bank");
  };

  return (
    <div className="border border-b-2 ">
      <div className="bg-[#ECECED] w-full flex items-center justify-center">
        <div className="w-[75%] py-6">
          <div className=" border-b pb-1 border-gray-400 mb-3 ">
            <h1 className="text-[#333333] font-semibold text-[13px] mb-2">
              Channel Red *New*
            </h1>
            <p className="text-[#676869] text-[13px]">
              <Link href="#">Mobile Banking</Link> |
              <Link href="#">Net Banking</Link> |
              <Link href="#">Manage your account</Link> |
              <Link href="#">Transfer money</Link> |
              <Link href="#">Recharge / Make payments</Link> |
              <Link href="/credit">Credit Card Apply</Link> |
              <Link href="#">Debit Cards</Link> |<Link href="#">Loans</Link> |
              <Link href="#">National Pension Scheme</Link> |
              <Link href="#">Deposits</Link>
            </p>
          </div>
          <div className="  border-b pb-1 border-gray-400 mb-3">
            <h1 className="text-[#333333] font-semibold text-[13px] mb-2">
              Popular Products
            </h1>
            <p className="text-[#676869] text-[13px]">
              <Link href="#">Home Loan</Link> |
              <Link href="#">Personal Loan</Link> |
              <Link href="#">Savings Account</Link> |
              <Link href="#">Current Account</Link> |
              <Link href="/credit">Credit Card Apply</Link> |
              <Link href="#">Mutual Funds</Link> |
              <Link href="#">National Pension Scheme (NPS)</Link> |
              <Link href="#">Business Loan</Link> |
              <Link href="#">Zero Balance Savings Account</Link> |
              <Link href="#">Life Insurance</Link> |
              <Link href="#">Fixed Deposit</Link> |
              <Link href="#">Recurring Deposit</Link> |
              <Link href="#">Loan against property</Link>
            </p>
          </div>
          <div className="  border-b pb-1 border-gray-400 mb-3">
            <h1 className="text-[#333333] font-semibold text-[13px] mb-2">
              Help Center
            </h1>
            <p className="text-[#676869] text-[13px]">
              <Link href="#">Account</Link> |
              <Link href="#">Issue with Transactions</Link> |
              <Link href="/credit">Credit Card Apply</Link> |
              <Link href="#">811 Account</Link> |
              <Link href="#">Fund Transfer, Bill Payment & Recharge</Link> |
              <Link href="#">Loans</Link> |<Link href="#">FASTag</Link> |
              <Link href="#">
                Fixed Deposit (FD) and Recurring Deposit (RD)
              </Link>{" "}
              |<Link href="#">NRI Services</Link> |
              <Link href="#">
                My Profile - Mobile Number, Aadhaar, Email ID & Address
              </Link>{" "}
              |<Link href="#">Forex</Link> |
              <Link href="#">
                Insurance (Premium payments, Tax benefit etc)
              </Link>{" "}
              |
              <Link href="#">
                Investments (Scheme Issues, Dividend related)
              </Link>{" "}
              |<Link href="#">Working Capital</Link> |
              <Link href="#">
                KayMall - Flights, Hotels, Bus, Trains, Shopping
              </Link>
            </p>
          </div>
        </div>
      </div>
      <div className="bg-[#ECECED] w-full flex items-center justify-center mt-1 text-[13px] pb-10">
        <div className="md:w-[75%] py-6">
          <div className="flex gap-4">
            <div>
              <div className="mb-4">
                <ul className="text-[#676869]  flex flex-col gap-1 ">
                  <li>
                    <p className="text-black font-semibold mb-2">
                      <a href="#" target="_top">
                        About us
                      </a>
                    </p>
                  </li>

                  <li>
                    <a
                      href="/trust-bank/loan-auth"
                      className="text-blue-400 font-semibold"
                    >
                      Home Loan
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Media Centre
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Sustainability
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_blank">
                      Careers
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      DIFC Branch
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      GIFT Branch
                    </a>
                  </li>
                  <li>
                    <a
                      href="/trust-bank/loan-auth"
                      className="text-blue-400 font-semibold"
                    >
                      Home Loan
                    </a>
                  </li>
                </ul>
              </div>
              <div className="">
                <ul className="text-[#676869] flex flex-col gap-1  ">
                  <li>
                    <p className="text-black font-semibold mb-2">
                      <a href="#" target="_top">
                        Investor Relations
                      </a>
                    </p>
                  </li>

                  <li>
                    <a href="#" target="_top">
                      Overview
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Financials
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Governance
                    </a>
                  </li>
                  <li>
                    <a
                      href="/trust-bank/loan-auth"
                      className="text-blue-400 font-semibold"
                    >
                      Home Loan
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Disclosures <br />
                      Regulation 46 and 62
                    </a>
                  </li>
                </ul>
              </div>
            </div>
            <div className="">
              <div className="mb-4">
                <ul className="text-[#676869] flex flex-col gap-1 ">
                  <li>
                    <p className="text-black font-semibold mb-2">
                      <a href="#" target="_top">
                        Customer Service
                      </a>
                    </p>
                  </li>

                  <li>
                    <a href="#" target="_top">
                      Important Information
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Write to us
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Grievance Redressal
                    </a>
                  </li>
                  <li>
                    <a
                      href="/trust-bank/credit"
                      className="text-blue-400 font-semibold"
                    >
                      Credit Card Apply
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Banking Ombudsman
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Download Forms
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Service Requests
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Track Application Status
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Tips on safe Banking
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Doorstep Banking Service
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Contact Us for Depository Services
                    </a>
                  </li>
                </ul>
              </div>
              <div className="">
                <ul className="text-[#676869] flex flex-col gap-1 ">
                  <li>
                    <p className="text-black font-semibold mb-2">
                      <a href="#" target="_top">
                        Aadhaar Services
                      </a>
                    </p>
                  </li>

                  <li>
                    <a
                      href="/trust-bank/credit"
                      className="text-blue-400 font-semibold"
                    >
                      Credit Card Apply
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Aadhaar Enrollment Center
                    </a>
                  </li>
                </ul>
              </div>
            </div>
            <div className="">
              <div className="">
                <ul className="text-[#676869] flex flex-col gap-1 ">
                  <li>
                    <p className="text-black font-semibold mb-2">
                      <a href="#" target="_top">
                        Calcutators & Tools
                      </a>
                    </p>
                  </li>

                  <li>
                    <a href="#" target="_top">
                      Personal Loan EMI Calculator
                    </a>
                  </li>
                  <li>
                    <a
                      href="/trust-bank/insurance"
                      className="text-blue-400 font-semibold"
                    >
                      Insurance
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Home Loan EMI Calculator
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Fixed Deposit Calculator
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Recurring Deposit Calculator
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Life Insurance Calculator
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Business Loan EMI Calculator
                    </a>
                  </li>
                  <li>
                    <a
                      href="/trust-bank/insurance"
                      className="text-blue-400 font-semibold"
                    >
                      Insurance
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Simple Interest Calculator
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Compound Interest Calculator
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Goal Planner
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Free Credit Score Checker
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Sip Calculator
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Mutual Fund Calculator
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Lump Sum Calculator
                    </a>
                  </li>
                </ul>
              </div>
            </div>
            <div className="flex gap-3">
              <div className="">
                <ul className="text-[#676869] flex flex-col gap-1 ">
                  <li>
                    <p className="text-black font-semibold mb-4">
                      <a href="#" target="_top">
                        Digital Banking
                      </a>
                    </p>
                  </li>

                  <li>
                    <a
                      href="/trust-bank/register"
                      className="text-blue-400 font-semibold"
                    >
                      Register
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Insta Services
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Business & Fintech
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Open Banking
                    </a>
                  </li>
                </ul>
                <ul className="text-[#676869] flex flex-col gap-1 mt-4">
                  <li>
                    <p className="text-black font-semibold mb-2">
                      <a href="#" target="_top">
                        Self Help
                      </a>
                    </p>
                  </li>

                  <li>
                    <a href="#" target="_top">
                      Help Center
                    </a>
                  </li>
                </ul>
                <ul className="text-[#676869] flex flex-col gap-1 mt-4 ">
                  <li>
                    <p className="text-black font-semibold mb-2 ">
                      <a href="#" target="_top">
                        Trending Products
                      </a>
                    </p>
                  </li>

                  <li>
                    <a
                      href="/trust-bank/register"
                      className="text-blue-400 font-semibold"
                    >
                      Register
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Digital Savings Bank Account
                    </a>
                  </li>
                </ul>
              </div>
              <div className="">
                <ul className="text-[#676869] flex flex-col gap-1 ">
                  <li>
                    <p className="text-black font-semibold mb-4">
                      <a href="#" target="_top">
                        Rates & fees
                      </a>
                    </p>
                  </li>

                  <li>
                    <a href="#" target="_top">
                      Interest Rates
                    </a>
                  </li>
                  <li>
                    <a
                      href="/trust-bank/preference-center"
                      className="text-blue-400 font-semibold"
                    >
                      Preference Center
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Goods & Services Tax (GST)
                    </a>
                  </li>
                </ul>
                <ul className="text-[#676869] flex flex-col gap-1 mt-4">
                  <li>
                    <p className="text-black font-semibold mb-4">
                      <a href="#" target="_top">
                        Financial Inclusion
                      </a>
                    </p>
                  </li>
                </ul>
                <ul className="text-[#676869] flex flex-col gap-1 mb-4">
                  <li>
                    <a
                      href="/trust-bank/preference-center"
                      className="text-blue-400 font-semibold "
                    >
                      Preference Center
                    </a>
                  </li>
                </ul>
                <ul className="text-[#676869] flex flex-col gap-1 ">
                  <li>
                    <p className="text-black font-semibold mb-2">
                      <a href="#" target="_top">
                        Erstwhile ING Vysya
                      </a>
                    </p>
                  </li>

                  <li>
                    <a href="#" target="_top">
                      Savings Account
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Current Account
                    </a>
                  </li>
                  <li>
                    <a
                      href="/trust-bank/preference-center"
                      className="text-blue-400 font-semibold"
                    >
                      Preference Center
                    </a>
                  </li>
                  <li>
                    <a href="#" target="_top">
                      Institutional Accounts
                    </a>
                  </li>
                </ul>
              </div>
            </div>
            <div className="">
              <ul className="text-[#676869] flex flex-col gap-1 ">
                <li>
                  <p className="text-black font-semibold mb-2">
                    <a href="#" target="_top">
                      Others
                    </a>
                  </p>
                </li>

                <li>
                  <a href="#" target="_top">
                    Credit Card T&C
                  </a>
                </li>
                <li>
                  <a href="#" target="_top">
                    Debit Card T&C
                  </a>
                </li>
                <li>
                  <a href="#" target="_top">
                    Co Brand Credit Card
                  </a>
                </li>
                <li>
                  <a href="#" target="_top">
                    Public Notice
                  </a>
                </li>
                <li>
                  <a href="#" target="_top">
                    Regulatory Disclosure
                  </a>
                </li>
                <li>
                  <a href="#" target="_top">
                    MSME Policy & Regulatory Updates
                  </a>
                </li>
                <li>
                  <a href="#" target="_top">
                    USA Patriot Act Certification
                  </a>
                </li>
                <li>
                  <a href="#" target="_top">
                    Subscriptions/ Recurring Payments
                  </a>
                </li>
                <li>
                  <a href="#" target="_top">
                    Wolfsberg AML Questionnaire
                  </a>
                </li>
                <li>
                  <a href="#" target="_top">
                    Auction Cum Sale Notice
                  </a>
                </li>
                <li>
                  <a href="#" target="_top">
                    Asset Classification Norms
                  </a>
                </li>
                <li>
                  <a href="#" target="_top">
                    Recovery Agent
                  </a>
                </li>
              </ul>
              <button
                onClick={removeLocalStorage}
                className="text-blue-400 font-semibold"
              >
                Clear Cookies
              </button>
            </div>
          </div>
        </div>
      </div>
      <div className="bg-[#dfdfe0] flex items-center justify-center py-3 text-[13px] relative">
        {/* <div className="absolute top-0 right-0 ">
          <div className="text-gray-100">This is a training or testing environment. No real banking services are provided.</div>
          <div className="text-gray-100">This site is a mimicry and not associated with any actual bank. For educational purposes only.</div>
        </div> */}

        <div className="w-[75%] text-[#676869]">
          <span className=" ">Copyright Trust Bank Limited.</span>
          <span className="mx-2">|</span>
          <Link href="#" target="_top" className=" hover:underline">
            Disclaimer
          </Link>
          <span className="mx-2">|</span>
          <Link href="#" target="_top" className=" hover:underline">
            Privacy Policy
          </Link>
          <span className="mx-2">|</span>
          <Link href="#" target="_top" className=" hover:underline">
            Terms &amp; Conditions
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Footer;
