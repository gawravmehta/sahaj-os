import React from "react";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

const cn = (...classes) => twMerge(clsx(...classes));

const Button = ({
  variant = "primary",
  className,
  children,
  onClick,
  btnLoading = false,
  disabled = false,
  ...props
}) => {
  const baseStyles = " rounded-full transition duration-300";

  const variantStyles = {
    primary:
      "bg-primary hover:bg-hover  cursor-pointer rounded-none text-white h-8 text-sm   flex items-center justify-center px-2",
    secondary:
      "border border-primary hover:bg-[#F2F9FF] cursor-pointer hover:border-[#F2F9FF] h-8 rounded-none text-sm text-primary   shadow-sm  flex justify-center items-center px-3 ",
    tertiary:
      " text-[#66afff] border border-[#66afff] hover:bg-[#66afff] hover:text-white rounded-none cursor-pointer  text-sm  h-8  px-3 flex items-center justify-center px-2",
    cancel:
      "flex items-center gap-2 px-3 py-1.5 text-sm text-[#d94e4e] hover:bg-[#fbeaea] hover:text-[#d94e4e] rounded-none",
    delete:
      "flex items-center gap-2 px-3 py-1.5 h-8 text-sm text-[#d94e4e] justify-center hover:bg-[#fbeaea] border border-[#d94e4e] hover:border-opacity-0 rounded-none",

    ghost:
      "bg-[#F0F4FF] text-[#757D94] rounded-none cursor-pointer  text-sm  h-8 px-3 flex items-center justify-center px-2",
    stepper:
      "bg-[#F0F4FF] text-[#757D94] rounded-none cursor-pointer  text-sm  h-8 px-3 flex items-center justify-center px-2",
    stepperPrimary:
      "bg-primary hover:bg-hover cursor-pointer rounded-none text-white h-8 text-sm   flex items-center justify-center px-2",
    back: " text-primary px-3 py-2 cursor-pointer text-sm  flex items-center gap-2 hover:bg-[#F2F9FF] rounded-none",
    deleteIcon: "text-[#757d94] hover:text-[#d94e4e]",
    close: "text-red-500 hover:text-red-600 text-[18px]",
    yes: "bg-red-500 px-8 py-1.5 text-white rounded-none",
    no: "border border-[#C7CFE2] px-6 py-1 rounded-none",
  };

  const buttonClasses = cn(
    baseStyles,
    variantStyles[variant],
    disabled && "cursor-not-allowed opacity-60",
    className,
    ` ${btnLoading && "relative"}`
  );

  return (
    <button
      {...props}
      className={buttonClasses}
      onClick={onClick}
      disabled={disabled || btnLoading}
    >
      {btnLoading && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div
            className={`h-4 w-4 animate-spin rounded-full border-2 ${
              variant === "primary" && "border-primary"
            } ${variant === "secondary" && "border-primary"} ${
              variant === "primary" && "border-white"
            } ${variant === "tertiary" && "border-primary"} ${
              variant === "cancel" && "border-[#d94e4e]"
            } border-t-transparent`}
          />
        </div>
      )}

      <span
        className={btnLoading ? "invisible" : "visible flex items-center gap-1"}
      >
        {children}
      </span>
    </button>
  );
};

export default Button;
