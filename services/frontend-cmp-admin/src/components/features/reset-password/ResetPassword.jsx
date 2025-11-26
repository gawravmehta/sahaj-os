"use client";
import React, { useState } from "react";
import Image from "next/image";

import { HiArrowNarrowRight } from "react-icons/hi";
import Link from "next/link";

import Button from "../../ui/Button";
import { RxLockClosed, RxLockOpen1 } from "react-icons/rx";

const ResetPassword = ({
  heading,
  pword,
  enterpw,
  password,
  setPassword,
  confirm_password,
  setConfirm_password,
  confirm,
  onClick,
  showLogin = false,
  loading,
}) => {
  const [eye, setEye] = useState(true);
  const [eyeOpen, setEyeOpen] = useState(true);

  const passwordEye = () => {
    setEye(!eye);
  };

  const passwordOpenEye = () => {
    setEyeOpen(!eyeOpen);
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-[url('/assets/bg-images/Bg-48-percent-opacity.png')] bg-cover bg-center">
      <div className="mb-8">
        <Image
          src="/assets/sahaj-logos/sahaj.png"
          alt="logo"
          width={150}
          height={150}
          className="h-9 w-40 object-contain"
        />
      </div>
      <div className="w-[420px] bg-background p-6 pb-10 shadow-[0_4px_16px_rgba(0,47,167,0.1)]">
        <form className="font-medium">
          <div className="mb-6">
            <h2 className="text-2xl font-semibold">{heading}</h2>
            <p className="text-xs text-subText">
              Create a secure password to protect your account.
            </p>
          </div>

          <div className="flex flex-col gap-2 text-sm">
            <label htmlFor={pword}>{pword}</label>
            <div className="relative flex w-full items-center bg-[#FDFDFD] ">
              <input
                className="h-9 w-full border bg-[#FDFDFD] pl-2 pr-8 text-sm outline-none placeholder:text-xs hover:border-primary focus:border-primary"
                value={password}
                type={eye ? "password" : "text"}
                id="password"
                name={pword}
                placeholder="Enter Password"
                onChange={(e) => setPassword(e.target.value)}
              />
              <Button
                type="button"
                variant="text"
                onClick={passwordEye}
                className="absolute right-2 text-[#c8c8c8]"
              >
                {eye ? <RxLockClosed size={20} /> : <RxLockOpen1 size={20} />}
              </Button>
            </div>
          </div>

          <div className="mt-[18px] flex flex-col gap-2 text-sm">
            <label htmlFor={enterpw}>{enterpw}</label>
            <div className="relative flex w-full items-center bg-[#FDFDFD] focus-within:border-borderPrimary">
              <input
                className="h-9 w-full border bg-[#FDFDFD] pl-2 pr-8 text-sm outline-none placeholder:text-xs hover:border-primary focus:border-hover"
                value={confirm_password}
                type={eyeOpen ? "password" : "text"}
                id="password"
                name={enterpw}
                placeholder="Confirm Password"
                onChange={(e) => setConfirm_password(e.target.value)}
              />
              <Button
                type="button"
                variant="text"
                onClick={passwordOpenEye}
                className="absolute right-2 text-[#c8c8c8]"
              >
                {eyeOpen ? (
                  <RxLockClosed size={20} />
                ) : (
                  <RxLockOpen1 size={20} />
                )}
              </Button>
            </div>
          </div>

          <div className="mt-8 flex justify-center">
            <Button
              variant={`${
                password.trim() === "" || confirm_password.trim() === ""
                  ? "ghost"
                  : "primary"
              }`}
              type="button"
              onClick={onClick}
              className="h-10 w-full"
            >
              {loading ? "Loading..." : confirm}
            </Button>
          </div>

          {showLogin && (
            <div className="mt-14 flex items-center justify-center gap-1 text-sm">
              <p className="text-subText">Remember Password?</p>
              <Link
                href="/auth/login"
                className="flex items-center gap-1 text-primary"
              >
                Login In
                <HiArrowNarrowRight size={17} className="-mb-[3px]" />
              </Link>
            </div>
          )}
        </form>
      </div>
    </div>
  );
};

export default ResetPassword;
