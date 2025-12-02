"use client";

import Image from "next/image";
import { FaYoutube } from "react-icons/fa6";
import { FaInstagramSquare } from "react-icons/fa";
import { FaLinkedin } from "react-icons/fa";
import { FaTwitter } from "react-icons/fa6";
import { FaFacebook } from "react-icons/fa";
import { LuSendHorizonal } from "react-icons/lu";
import Link from "next/link";

const Footer = () => {
  return (
    <footer className="flex flex-col" id="footer">
      <div className="bg-gray-100 container-fluid flex justify-center gap-16 py-10 px-10 mt-20 w-[100vw] m-auto">
        <div className="">
          <a
            href="/"
            className="flex items-center space-x-3 rtl:space-x-reverse"
          >
            <span className="self-center text-2xl font-semibold whitespace-nowrap">
              <span className="text-blue-600">Health</span>Care
            </span>
          </a>
          <div className="pt-9 pb-8">
            <h2 className="pb-5 text-lg font-medium text-gray-700">
              Connect With Us
            </h2>
            <ul className="flex">
              <li className="mr-6">
                <a
                  className="inline-block"
                  aria-label="facebook"
                  target="_blank"
                  href="https://www.facebook.com/"
                >
                  <FaFacebook size={30} />
                </a>
              </li>
              <li className="mr-6">
                <a
                  className="inline-block"
                  aria-label="twitter"
                  target="_blank"
                  href="https://twitter.com"
                >
                  <FaTwitter size={30} />
                </a>
              </li>
              <li className="mr-6">
                <a
                  className="inline-block"
                  aria-label="linkedin"
                  target="_blank"
                  href="https://in.linkedin.com/"
                >
                  <FaLinkedin size={30} />
                </a>
              </li>
              <li className="mr-6">
                <a
                  className="inline-block"
                  aria-label="instagram"
                  target="_blank"
                  href="https://www.instagram.com"
                >
                  <FaInstagramSquare size={30} />
                </a>
              </li>
              <li>
                <a
                  className="inline-block"
                  aria-label="youtube"
                  target="_blank"
                  href="https://www.youtube.com"
                >
                  <FaYoutube size={30} />
                </a>
              </li>
            </ul>
          </div>
          <span className="text-lg font-medium text-gray-700 pb-1">
            Subscribe To Our Newsletter
          </span>
          <span className="subscribe-field flex justify-between items-center mt-4 bg-white px-4 py-3">
            <input
              id="newsLetter"
              className="subscribe-field-textfield w-1/10 text-lg font-medium outline-none w-full"
              placeholder="Enter your email ID"
              type="text"
              name="newsLetter"
            />
            <button
              type="button"
              className=""
              aria-label="send color--grey-one button"
            >
              <LuSendHorizonal size={30} />
            </button>
          </span>
          <span className="text-red-500 text-sm mt-1 font-medium"></span>
          <div className="flex flex-col mt-10">
            <div>
              <h2 className="mb-4 text-lg text-gray-700">Download The App</h2>
              <div className="flex">
                <a className="mr-4" href="#">
                  <Image
                    alt="playstore image"
                    width={175}
                    height={75}
                    src="https://stgaccinwbsdevlrs01.blob.core.windows.net/newcorporatewbsite/settings/October2023/jXCuKcKE6TlEp40kFSaB.webp?w=384&q=75"
                    className="text-transparent"
                  />
                </a>
                <a href="#">
                  <Image
                    alt="appstore image"
                    width={175}
                    height={75}
                    src="https://stgaccinwbsdevlrs01.blob.core.windows.net/newcorporatewbsite/settings/October2023/skqwzEax9ovi5QguZu6q.webp?w=384&q=75"
                    className="text-transparent"
                  />
                </a>
              </div>
            </div>
            <div id="qr-code" className=""></div>
          </div>
        </div>
        <div className="mt-5 ml-1">
          <h2 className="font-bold text-lg text-gray-700">Patient Guide</h2>
          <ul>
            <li className="pt-4">
              <a
                className="text-base font-medium text-gray-700"
                href="/find-a-doctor"
              >
                Find a Doctor
              </a>
            </li>
            <li className="pt-4">
              <a className="text-base font-medium text-gray-700" href="#">
                Our Network
              </a>
            </li>
            <li className="pt-4">
              <a className="text-base font-medium text-gray-700" href="#">
                Video Consultation
              </a>
            </li>
            <li className="pt-4">
              <a
                className="text-base font-medium text-blue-700"
                href="book_appointment"
              >
                Book an Appointment
              </a>
            </li>
            <li className="pt-4">
              <a className="text-base font-medium text-gray-700" href="#">
                Make an Enquiry
              </a>
            </li>
            <li className="pt-4">
              <a className="text-base font-medium text-gray-700" href="#">
                Feedback
              </a>
            </li>
            <li className="pt-4">
              <a className="text-base font-medium text-gray-700" href="#">
                Health Check Package
              </a>
            </li>
          </ul>
        </div>
        <div className="mt-5 ml-1">
          <h2 className="font-bold text-lg text-gray-700">What We Treat</h2>
          <ul>
            <li className="pt-4">
              <a className="text-base font-medium text-gray-700" href="#">
                Chest Pain
              </a>
            </li>
            <li className="pt-4">
              <a className="text-base font-medium text-gray-700" href="#">
                Heart Attack
              </a>
            </li>
            <li className="pt-4">
              <a className="text-base font-medium text-gray-700" href="#">
                Varicose Veins
              </a>
            </li>
            <li className="pt-4">
              <a className="text-base font-medium text-gray-700" href="#">
                Thyroid Problems
              </a>
            </li>
            <li className="pt-4">
              <a className="text-base font-medium text-gray-700" href="#">
                View All
              </a>
            </li>
          </ul>
        </div>
        <div className="mt-5 ml-1">
          <h2 className="font-bold text-lg text-gray-700">
            For Medical Professionals
          </h2>
          <ul>
            <li className="pt-4">
              <a className="text-base font-medium text-gray-700" href="#">
                Academics
              </a>
            </li>
            <li className="pt-4">
              <a className="text-base font-medium text-gray-700" href="#">
                Clinical Research
              </a>
            </li>
            <li className="pt-4">
              <a
                className="text-base font-medium text-blue-700"
                href="/health_care/services"
              >
                Services
              </a>
            </li>
            <li className="pt-4">
              <a
                className="text-base font-medium text-blue-700"
                href="/health_care/preference_center"
              >
                Preference Center
              </a>
            </li>
          </ul>
        </div>
        <div className="mt-5 ml-1">
          <h2 className="font-bold text-lg text-gray-700">Company</h2>
          <ul>
            <li className="pt-4">
              <a className="text-base font-medium text-gray-700" href="#">
                About Us
              </a>
            </li>
            <li className="pt-4">
              <a className="text-base font-medium text-gray-700" href="#">
                Leadership
              </a>
            </li>
            <li className="pt-4">
              <a className="text-base font-medium text-gray-700" href="#">
                Stakeholder Relations
              </a>
            </li>
            <li className="pt-4">
              <a className="text-base font-medium text-gray-700" href="#">
                News & Media Relations
              </a>
            </li>
            <li className="pt-4">
              <a className="text-base font-medium text-gray-700" href="#">
                Careers
              </a>
            </li>
            <li className="pt-4">
              <a className="text-base font-medium text-gray-700" href="#">
                CSR
              </a>
            </li>
            <li className="pt-4">
              <a className="text-base font-medium text-gray-700" href="#">
                Contact Us
              </a>
            </li>
          </ul>
        </div>
        <div className="mt-5 ml-1">
          <h2 className="font-bold text-lg text-gray-700">International</h2>
          <ul>
            <li className="pt-4">
              <a className="text-base font-medium text-gray-700" href="#">
                International Patientcare
              </a>
            </li>
          </ul>
        </div>
      </div>
      <div className="flex pb-8 container-fluid justify-between pt-5">
        <ul className="flex">
          <li className="p-1">
            <a
              className="mr-5 text-gray-500 text-sm font-medium pl-10"
              target="_blank"
              href="#"
            >
              NPPA Implant Pricing
            </a>
          </li>
          <li className="p-1">
            <a className="mr-5 text-gray-500 text-sm font-medium" href="#">
              Terms & Conditions
            </a>
          </li>
          <li className="p-1">
            <a className="mr-5 text-gray-500 text-sm font-medium" href="#">
              Privacy Policy
            </a>
          </li>
          <li className="p-1">
            <a className="mr-5 text-gray-500 text-sm font-medium" href="#">
              Disclaimer
            </a>
          </li>
          <li onClick={() => localStorage.clear()} className="p-1">
            <a
              href="/health_care"
              className="mr-5 text-blue-700 text-sm font-medium"
            >
              Clear Cookie
            </a>
          </li>
        </ul>

        <span className="p-1 text-gray-500 font-medium text-sm pr-10">
          <Link
            href="/health_care"
            className=" items-center space-x-3 rtl:space-x-reverse"
          >
            <span className="self-center text-2xl font-semibold whitespace-nowrap pr-4">
              <span className="text-blue-600">Health</span>Care
            </span>{" "}
          </Link>
          © Ltd | All Rights Reserved
        </span>
      </div>
      <div className="container-fluid"></div>
    </footer>
  );
};

export default Footer;
