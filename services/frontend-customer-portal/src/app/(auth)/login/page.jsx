"use client";

import Image from "next/image";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState } from "react";
import { AiOutlineMail } from "react-icons/ai";
import { MdOutlineLocalPhone } from "react-icons/md";
import { apiCall } from "@/hooks/apiCall";
import Cookies from "js-cookie";
import toast from "react-hot-toast";
import Button from "@/components/ui/Button";
import { getErrorMessage } from "@/utils/errorHandler";
import Link from "next/link";
import { langOptions, loginTranslations } from "@/constants/translations";

const Page = () => {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [mobile, setMobile] = useState("");
  const [isEmailLogin, setIsEmailLogin] = useState(true);
  const [isLoading, setIsLoading] = useState(false);

  const searchParams = useSearchParams();
  const agreementId = searchParams.get("agreement_id");

  const [lang, setLang] = useState("en");
  const t = loginTranslations[lang];

  const loginUser = async (e) => {
    e.preventDefault();

    if (isEmailLogin && !email) {
      toast.error("Please enter email address");
      return;
    }
    if (!isEmailLogin && !mobile) {
      toast.error("Please enter mobile number");
      return;
    }

    setIsLoading(true);
    try {
      const response = await apiCall("/api/v1/auth/login-preference-center", {
        method: "POST",
        params: {
          email: isEmailLogin ? email : "",
          mobile: isEmailLogin ? "" : mobile,
        },
      });

      if (!response || !response.success) {
        throw new Error(response?.message || "Invalid response from server");
      }

      Cookies.set("access_token", response.access_token || "temp_token", {
        expires: 1,
      });
      Cookies.set("email", email, { expires: 1 });
      Cookies.set("mobile", mobile, { expires: 1 });

      toast.success(response.message);
      if (agreementId) {
        router.push(`/verify-otp?agreement_id=${agreementId}`);
      } else {
        router.push(`/verify-otp`);
      }
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (setter) => (e) => {
    const value = e.clipboardData?.getData("text") || e.target.value;
    setter(value.trim());
  };

  return (
    <Suspense fallback={<div>Loading...</div>}>
      <div className="flex flex-col items-center justify-end">
        <div className="flex flex-col h-screen items-center  justify-center  px-4">
          <div className="mb-6 flex justify-center">
            <Image
              src="/concur-logo/logo-first.png"
              alt="logo"
              width={150}
              height={150}
              className="h-9 w-40 object-contain"
            />
          </div>
          <div className="flex w-full max-w-4xl  bg-[#FBFCFE] shadow-lg ">
            <div className="hidden w-1/2 flex-col pt-10 px-8  sm:flex">
              <h1 className=" text-[24px] text-[#000000] ">{t.infoTitle}</h1>
              <h1 className="text-[#505050] text-[12px]">{t.infoDesc}</h1>
              <h1 className="pt-2 text-[#3F3F3F] text-[14px]">
                {t.yourRightsTitle}
              </h1>
              <ul className="space-y-3 text-base text-gray-600 py-5 list-inside list-disc ">
                {t.rightsList.map((text, i) => (
                  <li key={i}>{text}</li>
                ))}
              </ul>
              <Link
                target="_blank"
                href="https://news.concur.live/"
                className="text-[#484848] font-normal underline hover:text-blue-900 "
              >
                {t.viewMore}
              </Link>
            </div>

            <div className="w-full px-8 py-10 sm:w-1/2">
              <form onSubmit={loginUser} className=" bg-[#FFFFFF] py-8 px-5">
                <h2 className="text-2xl font-semibold">{t.login}</h2>
                <p className="text-subText text-[12px] font-">
                  {t.secureText}{" "}
                </p>
                {isEmailLogin ? (
                  <div className="flex flex-col gap-2 text-sm mt-3">
                    <label htmlFor="email" className="text-text text-[14px]">
                      {t.emailLabel}
                    </label>
                    <div className="relative flex w-full items-center bg-[#FDFDFD]">
                      <input
                        className="h-10 w-full border bg-[#FDFDFD] pl-2 pr-8 text-sm outline-none placeholder:text-xs hover:border-primary focus:border-primary"
                        type="email"
                        value={email}
                        id="email"
                        name="email"
                        placeholder={t.emailPlaceholder}
                        onChange={(e) => setEmail(e.target.value)}
                      />
                      <AiOutlineMail
                        size={20}
                        className="absolute right-2 text-[#c8c8c8]"
                      />
                    </div>
                  </div>
                ) : (
                  <div className="flex flex-col gap-2 text-sm mt-3">
                    <label htmlFor="mobile" className="text-text text-[14px]">
                      {t.mobileLabel}
                    </label>
                    <div className="relative flex w-full items-center border bg-[#FDFDFD] hover:border-primary focus:border-primary">
                      <input
                        className="h-10 w-full bg-[#FDFDFD] pl-2 pr-8 text-sm outline-none placeholder:text-xs"
                        value={mobile}
                        type="tel"
                        id="mobile"
                        name="mobile"
                        placeholder={t.mobilePlaceholder}
                        onChange={handleInputChange(setMobile)}
                        onInput={handleInputChange(setMobile)}
                        onPaste={handleInputChange(setMobile)}
                      />
                      <MdOutlineLocalPhone
                        size={18}
                        className="absolute right-2 text-[#c8c8c8]"
                      />
                    </div>
                  </div>
                )}

                <Button
                  btnLoading={isLoading}
                  variant={
                    (isEmailLogin ? email : mobile) ? "primary" : "ghost"
                  }
                  className="h-10 w-full text-base mt-7"
                  type="submit"
                  disabled={isLoading || !(isEmailLogin ? email : mobile)}
                >
                  {isLoading ? "Sending OTP..." : t.button1}
                </Button>

                <div className="flex items-center gap-1 py-3">
                  <div className="w-40 h-0.5 bg-[#DDDDDD]"></div>
                  <span className="text-subHeading">{t.orText}</span>
                  <div className="w-40 h-0.5 bg-[#DDDDDD]"></div>
                </div>
                <div className="text-center w-full mt-3 ">
                  <Button
                    variant="secondary"
                    type="button"
                    onClick={() => setIsEmailLogin(!isEmailLogin)}
                    className="w-full h-10"
                    disabled={isEmailLogin}
                  >
                    {isEmailLogin ? t.button2 : t.button3}
                  </Button>
                </div>
              </form>
            </div>
          </div>
        </div>
        <div className="-mt-5 flex flex-wrap absolute bottom-7 mx-auto justify-center gap-10 text-sm text-gray-600">
          {langOptions.map((lng) => (
            <button
              key={lng.code}
              onClick={() => setLang(lng.code)}
              className={`${
                lang === lng.code
                  ? "font-semibold text-black"
                  : "hover:text-primary"
              } cursor-pointer hover:font-semibold  `}
            >
              {lng.label}
            </button>
          ))}
        </div>
      </div>
    </Suspense>
  );
};

export default Page;
