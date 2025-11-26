import React from "react";
import { RxCross2 } from "react-icons/rx";

const Tag = ({
  label,
  variant = "default",
  removable = false,
  className = "text-xs",
  onRemove,
  onClick = () => {},
}) => {
  const baseStyles =
    " items-center flex justify-center border rounded-full px-4 py-1 text-center font-medium text-nowrap";

    const variants = {
      default: "bg-[#E9E9E9] text-[#727272] border-transparent",
      lightBlue: "bg-[#F2F9FF] text-[#66AFFF] border-transparent",
      outlineBlue: "border-[#3C3D64] text-[#3C3D64] bg-transparent",
      solidBlue: "bg-[#3C3D64] text-white border-transparent",
      inactive: "bg-[#FBEAEA] text-[#D94E4E] border-transparent",
      active: "bg-[#E1FFE7] text-[#06A42A] border-transparent",
      suspended: "bg-[#FEF7DE] text-[#A18C00] border-transparent",
      draft: "bg-[#E9E9E9] text-[#727272] border-transparent",
    };

  return (
    <div
      onClick={onClick}
      className={`${baseStyles} ${variants[variant] || ""} ${className}`}
    >
      <span className="">{label}</span>
      {removable && (
        <button
          onClick={onRemove}
          className="ml-2 text-[#d94e4e] hover:text-[#727272]"
        >
          <RxCross2 size={14} />
        </button>
      )}
    </div>
  );
};

export default Tag;
