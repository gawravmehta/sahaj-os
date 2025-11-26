import Image from "next/image";
import React, { useState } from "react";
import { FiChevronDown, FiChevronUp } from "react-icons/fi";
import NoDataFound from "@/components/ui/NoDataFound";

const AccordionItem = ({ initialMessages }) => {
  const [isOpen, setIsOpen] = useState(false);

  const formatDate = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString("en-US", {
      day: "numeric",
      month: "short",
      year: "numeric",
    });
  };

  return (
    <div className="relative mb-3 w-full border-b border-borderheader p-3">
      <div
        className="flex cursor-pointer items-center"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="shrink-0">
          <Image
            src={initialMessages.sender_image || "/default-avatar.png"}
            alt="Profile Picture"
            width={100}
            height={100}
            className="size-14 rounded-full border bg-white object-contain p-2"
          />
        </div>
        <div className="ml-4 min-w-0 flex-1">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            <h4 className="truncate text-lg font-semibold text-gray-800">
              {initialMessages.sender}
            </h4>

            <p className="mt-2 flex items-center text-sm text-gray-500">
              <span
                className={`mr-2 inline-block h-2 w-2 rounded-full ${
                  initialMessages.status === "sent"
                    ? "bg-blue-500"
                    : initialMessages.status === "delivered"
                    ? "bg-green-500"
                    : "bg-gray-500"
                }`}
              ></span>
              Status: {initialMessages.status}
            </p>
          </div>
          <div className="mt-1 flex items-center justify-between">
            <p className="text-sm text-gray-500">{initialMessages.subject}</p>
            {isOpen ? (
              <FiChevronUp className="text-gray-500" />
            ) : (
              <FiChevronDown className="text-gray-500" />
            )}
          </div>
        </div>
      </div>

      {isOpen && (
        <div className="mt-3 pl-[75px]">
          <p className="whitespace-pre-wrap text-sm text-gray-600">
            {initialMessages.message}
          </p>
          <p className="text-xs text-gray-500">
            {formatDate(initialMessages.timestamp)}
          </p>
        </div>
      )}
    </div>
  );
};

const Message = ({ data }) => {
  const initialMessages =
    data?.request_conversation || data?.request_conversation || [];

  if (!initialMessages || initialMessages.length === 0) {
    return (
      <div className="container mx-auto flex h-[calc(100vh-180px)] flex-col items-center justify-center p-6">
        <NoDataFound />
      </div>
    );
  }

  return (
    <div className="custom-scrollbar container mx-auto mt-5 flex h-[calc(100vh-180px)] w-[40%] flex-col items-center overflow-y-auto">
      <div className="flex w-full justify-end"></div>

      <div className="mb-5 flex w-full flex-col items-center">
        {initialMessages.map((initialMessages) => (
          <AccordionItem
            key={initialMessages.message_id}
            initialMessages={initialMessages}
          />
        ))}
      </div>
    </div>
  );
};

export default Message;
