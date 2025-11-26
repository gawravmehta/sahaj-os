"use client";

import * as React from "react";
import { OTPInput, OTPInputContext } from "input-otp";

function InputOTP({ className, containerClassName, ...props }) {
  return (
    <OTPInput
      data-slot="input-otp"
      containerClassName={`flex items-center gap-6  has-disabled:opacity-50 ${
        containerClassName || ""
      }`}
      className={`disabled:cursor-not-allowed ${className || ""}`}
      {...props}
    />
  );
}

function InputOTPGroup({ className, ...props }) {
  return (
    <div
      data-slot="input-otp-group"
      className={`flex items-center gap-10 ${className || ""}`}
      {...props}
    />
  );
}

function InputOTPSlot({ index, className, ...props }) {
  const inputOTPContext = React.useContext(OTPInputContext);
  const { char, hasFakeCaret, isActive } = inputOTPContext?.slots[index] ?? {};

  return (
    <div
      data-slot="input-otp-slot"
      data-active={isActive}
      className={`relative flex h-10 w-10  items-center justify-center text-base border border-primary  shadow transition-all outline-none focus-within:ring-2 focus-within:ring-red-500 ${
        className || ""
      }`}
      {...props}
    >
      {char}
      {hasFakeCaret && (
        <div className="pointer-events-none absolute inset-0 flex items-center justify-center gap-5">
          <div className="animate-caret-blink bg-primary h-5 w-px duration-1000" />
        </div>
      )}
    </div>
  );
}

export { InputOTP, InputOTPGroup, InputOTPSlot };
