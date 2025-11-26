"use client";

import logo from "@/../../public/assets/sahaj-logos/sahaj.png";
import { translations } from "@/constants/login";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import Cookies from "js-cookie";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useState } from "react";
import toast from "react-hot-toast";
import { AiOutlineMail } from "react-icons/ai";
import { RxLockClosed, RxLockOpen1 } from "react-icons/rx";

export default function LoginPage() {
  const router = useRouter();
  const [lang, setLang] = useState("en");
  const t = translations[lang];
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [eye, setEye] = useState(true);

  const isFormValid = email.trim() !== "" && password.trim() !== "";

  const passwordEye = () => setEye(!eye);

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!isFormValid) return;

    setLoading(true);

    try {
      const data = await apiCall("/auth/login", {
        method: "POST",
        data: { email, password },
      });

      Cookies.set("access_token", data.access_token, {
        secure: true,
        sameSite: "Strict",
      });
      Cookies.set("is_invited_user", data.is_invited_user ? "true" : "false", {
        secure: true,
        sameSite: "Strict",
      });      

      if (data?.is_password_reseted == false) {
        Cookies.set("isNotPasswordSet", "true", {
          secure: true,
          sameSite: "Strict",
        });
        Cookies.set("isNotOrgSetup", "true", {
          secure: true,
          sameSite: "Strict",
        });
        router.push(`/reset-password`);
        toast.success("Please reset your password.");
      } else if (data?.is_org_configured === false && data?.is_invited_user === false) {
        Cookies.set("isNotOrgSetup", "true", {
          secure: true,
          sameSite: "Strict",
        });
        router.push("/org-setup");
        toast.success("Please complete your organization setup.");
      }
       else {
        router.push("/apps");
        toast.success("Login successful!");
      }
    } catch (err) {
      setLoading(false);
      console.error("❌ Login failed:", err);
      const errorMessage = getErrorMessage(err);
      toast.error(errorMessage);
    }
  };

  return (
    <div className="relative flex min-h-screen flex-col items-center justify-center bg-[url('/assets/bg-images/Bg-48-percent-opacity.png')] bg-cover bg-center">
      <div className="flex w-full flex-col items-center justify-center sm:w-[450px]">
        <Image
          src={logo}
          alt="logo"
          width={150}
          height={150}
          className="h-9 w-40 object-contain"
          unoptimized={true}
        />

        <form
          onSubmit={handleLogin}
          className="mt-6 w-[90%] bg-background p-6 shadow-[0_4px_16px_rgba(0,47,167,0.1)] sm:w-[420px]"
        >
          <div className="mb-6">
            <h2 className="text-2xl font-semibold">{t.login}</h2>
            <p className="text-xs text-subText">{t.secureText}</p>
          </div>

          <div className="mb-[18px] flex flex-col gap-2 text-sm">
            <label htmlFor="email">{t.emailLabel}</label>
            <div className="relative flex w-full items-center bg-[#FDFDFD]">
              <input
                className="h-9 w-full border bg-[#FDFDFD] pl-2 pr-8 text-sm outline-none placeholder:text-xs hover:border-primary focus:border-primary"
                type="email"
                value={email}
                id="email"
                placeholder="example1234@domain.com"
                onChange={(e) => setEmail(e.target.value)}
                required
              />
              <AiOutlineMail
                size={20}
                className="absolute right-2 text-[#c8c8c8] hover:text-[#3C3D64]"
              />
            </div>
          </div>

          <div className="flex flex-col gap-2 text-sm">
            <label htmlFor="password">{t.passwordLabel}</label>
            <div className="relative flex w-full items-center border bg-[#FDFDFD] hover:border-primary focus:border-primary">
              <input
                className="h-9 w-full bg-[#FDFDFD] pl-2 pr-8 text-sm outline-none placeholder:text-xs"
                value={password}
                type={eye ? "password" : "text"}
                id="password"
                placeholder="••••••••"
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <span
                onClick={passwordEye}
                className="absolute right-2 text-[#c8c8c8]"
              >
                {eye ? (
                  <RxLockClosed
                    size={18}
                    className="cursor-pointer hover:text-primary"
                  />
                ) : (
                  <RxLockOpen1
                    size={18}
                    className="cursor-pointer text-primary"
                  />
                )}
              </span>
            </div>
          </div>

          <div className="mt-6">
            <button
              type="submit"
              disabled={!isFormValid || loading}
              className={`h-10 w-full text-base text-white transition cursor-pointer ${
                !isFormValid || loading
                  ? "bg-gray-300 cursor-not-allowed"
                  : "bg-primary hover:bg-hover"
              }`}
            >
              {loading ? "Logging in..." : t.button}
            </button>
          </div>
        </form>
      </div>
      <div className="mt-6 flex flex-wrap absolute bottom-7 mx-auto justify-center gap-10 text-sm text-gray-600">
        {[
          { code: "en", label: "English" },
          { code: "hi", label: "हिन्दी" },
          { code: "bn", label: "বাংলা" },
          { code: "te", label: "తెలుగు" },
          { code: "mr", label: "मराठी" },
          { code: "ta", label: "தமிழ்" },
          { code: "ur", label: "اردو" },
          { code: "gu", label: "ગુજરાતી" },
          { code: "kn", label: "ಕನ್ನಡ" },
          { code: "ml", label: "മലയാളം" },
          { code: "sa", label: "संस्कृत" },
          { code: "bho", label: "भोजपुरी" },
          { code: "mai", label: "मैथिली" },
          { code: "ks", label: "कश्मीरी" },
          { code: "or", label: "ଓଡ଼ିଆ" },
        ].map((lng) => (
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
  );
}
