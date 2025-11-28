"use client";

import Image from "next/image";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import { apiCall } from "@/hooks/apiCall";
import toast from "react-hot-toast";
import Cookies from "js-cookie";
import { getErrorMessage } from "@/utils/errorHandler";
import {
  InputOTP,
  InputOTPGroup,
  InputOTPSlot,
} from "@/components/ui/input-otp";

const Page = () => {
  const router = useRouter();
  const [otp, setOtp] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [resendLoading, setResendLoading] = useState(false);
  const [cooldown, setCooldown] = useState(30);
  const [isCooldownActive, setIsCooldownActive] = useState(true);

  const email = Cookies.get("email");
  const mobile = Cookies.get("mobile");

  const searchParams = useSearchParams();
  const agreementId = searchParams.get("agreement_id");

  useEffect(() => {
    let timer;
    if (isCooldownActive && cooldown > 0) {
      timer = setTimeout(() => setCooldown(cooldown - 1), 1000);
    } else if (cooldown === 0) {
      setIsCooldownActive(false);
    }
    return () => clearTimeout(timer);
  }, [cooldown, isCooldownActive]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (otp.length !== 6) {
      toast.error("Please enter the complete 6-digit OTP");
      return;
    }

    setIsLoading(true);

    try {
      const response = await apiCall("/api/v1/auth/validate-otp", {
        method: "POST",
        params: {
          email: email,
          otp: otp,
          df_id: process.env.NEXT_PUBLIC_DF_ID,
        },
      });

      toast.success(response?.message || "Login successful!");
      Cookies.set("access_token", response?.access_token);
      ["email", "mobile"].forEach((cookie) => Cookies.remove(cookie));
      if (agreementId) {
        router.push(
          `/manage-preference/update-preference?agreement_id=${agreementId}`
        );
      } else {
        router.push("/");
      }
    } catch (error) {
      toast.error(getErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  };

  const handleResendOtp = async () => {
    setResendLoading(true);
    try {
      if (!email) {
        toast.error("Email not found. Please login again.");
        return;
      }

      const response = await apiCall("/api/v1/auth/resend-otp", {
        method: "POST",
        params: { email },
      });

      if (response.success) {
        toast.success(response?.message || "New OTP sent successfully");
        setCooldown(30);
        setIsCooldownActive(true);
      } else {
        toast.error(response.message || "Failed to resend OTP");
      }
    } catch (error) {
      toast.error(error.message || "Error resending OTP");
    } finally {
      setResendLoading(false);
    }
  };

  return (
    <Suspense fallback={<div>Loading...</div>}>
      <div className="flex min-h-screen items-center justify-center bg-[url('/bg-images/Bg-48-percent-opacity.png')] bg-cover bg-center">
        <div className="flex w-full flex-col items-center justify-center sm:w-[450px]">
          <Image
            src="/concur-logo/logo-first.png"
            alt="logo"
            width={150}
            height={150}
            className="h-9 w-40 object-contain"
          />

          <form
            onSubmit={handleSubmit}
            className="mt-8  bg-[#FBFCFE] p-6 shadow-[0_4px_16px_rgba(0,47,167,0.1)]"
          >
            <div className="mb-6">
              <h2 className="text-2xl font-semibold">Verify OTP</h2>
              <p className="text-xs text-subText">
                <span className="font-sans font-medium text-primary">
                  Secure verification
                </span>{" "}
                for your{" "}
                <span className="font-sans font-medium text-primary">
                  account access.
                </span>
              </p>
            </div>

            <div className="mb-6">
              <p className="text-sm text-gray-600 mb-4">
                We've sent a 6-digit code to your email/mobile number
              </p>

              <InputOTP maxLength={6} value={otp} onChange={setOtp}>
                <InputOTPGroup>
                  <InputOTPSlot index={0} />
                  <InputOTPSlot index={1} />
                  <InputOTPSlot index={2} />
                </InputOTPGroup>
                <InputOTPGroup>
                  <InputOTPSlot index={3} />
                  <InputOTPSlot index={4} />
                  <InputOTPSlot index={5} />
                </InputOTPGroup>
              </InputOTP>
            </div>

            <div className="text-center text-sm mb-6">
              <p className="text-subText">Didn't receive code?</p>
              <button
                type="button"
                onClick={handleResendOtp}
                disabled={resendLoading || isCooldownActive}
                className={`text-primary font-medium ${
                  !(resendLoading || isCooldownActive) && "hover:underline"
                }`}
              >
                {resendLoading
                  ? "Sending..."
                  : isCooldownActive
                  ? `Resend OTP in ${cooldown}s`
                  : "Resend OTP"}
              </button>
            </div>

            <div className="mt-4 flex flex-col gap-3">
              <button
                type="submit"
                disabled={otp.length !== 6 || isLoading}
                className={`flex h-10 items-center justify-center text-base ${
                  otp.length !== 6 || isLoading
                    ? "bg-[#F0F4FF] text-[#757D94] cursor-not-allowed"
                    : "bg-primary hover:bg-hover cursor-pointer text-white"
                } transition-colors`}
              >
                {isLoading ? "Verifying..." : "Verify"}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Suspense>
  );
};

export default Page;
