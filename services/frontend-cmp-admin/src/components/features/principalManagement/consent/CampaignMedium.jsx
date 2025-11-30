import React from "react";
import { FaCircleCheck } from "react-icons/fa6";
import { MdOutlineEmail, MdOutlineTv, MdOutlineSms } from "react-icons/md";

export default function CampaignMedium({
  selectedMediums,
  setSelectedMediums,
}) {
  const mediums = [
    {
      label: "Email",
      Icon: MdOutlineEmail,
      desc: "Deliver campaign notice via e-mail",
      value: "email",
      isComingSoon: false,
    },
    {
      label: "In App",
      Icon: MdOutlineTv,
      desc: "Deliver consent notice in the app",
      value: "in-app",
      isComingSoon: true,
    },
    {
      label: "SMS",
      Icon: MdOutlineSms,
      desc: "Send campaign notice directly via SMS",
      value: "sms",
      isComingSoon: true,
    },
  ];

  const toggleMedium = (value, isComingSoon) => {
    if (isComingSoon) return;
    if (selectedMediums.includes(value)) {
      setSelectedMediums((prev) => prev.filter((m) => m !== value));
    } else {
      setSelectedMediums((prev) => [...prev, value]);
    }
  };

  return (
    <div className="mt-3">
      <div className="pb-3">
        <h2 className="text-[15px] ">Campaign Medium</h2>
      </div>

      <div className="flex justify-start items-stretch gap-6">
        {mediums.map((m) => {
          const isSelected = selectedMediums.includes(m.value);
          return (
            <div
              key={m.value}
              onClick={() => toggleMedium(m.value, m.isComingSoon)}
              className={`relative flex w-56 flex-col justify-start border p-4 shadow-sm transition-all ${
                m.isComingSoon
                  ? "cursor-not-allowed bg-gray-50 opacity-70"
                  : "cursor-pointer hover:shadow-md"
              } ${isSelected ? "border-blue-900" : "border-gray-300"}`}
            >
              {m.isComingSoon && (
                <span className="absolute right-2 top-2 rounded-full bg-gray-200 px-2 py-0.5 text-[10px] font-medium text-gray-600">
                  Coming Soon
                </span>
              )}

              {isSelected && !m.isComingSoon && (
                <FaCircleCheck
                  size={22}
                  className="absolute right-2 top-2 text-green-600 bg-white rounded-full"
                />
              )}
              <div className="flex justify-start gap-2 items-start">
                <m.Icon
                  size={22}
                  className={`mb-2 ${
                    m.isComingSoon ? "text-gray-400" : "text-blue-600"
                  }`}
                />
                <p
                  className={`font-medium ${
                    m.isComingSoon ? "text-gray-500" : ""
                  }`}
                >
                  {m.label}
                </p>
              </div>

              <p className="mt-1 text-sm text-gray-500">{m.desc}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}
