"use client";

import DataTable from "@/components/shared/data-table/DataTable";
import DateTimeFormatter from "@/components/ui/DateTimeFormatter";
import NoDataFound from "@/components/ui/NoDataFound";
import Tag from "@/components/ui/Tag";
import Image from "next/image";

import { MdDone, MdOutlineEmail, MdOutlineSms } from "react-icons/md";
import { RiComputerLine } from "react-icons/ri";
import { RxCross2 } from "react-icons/rx";

function ConsentMain({
  tableDataRows = [],
  loading,
  totalPages,
  currentPage,
  setCurrentPage,
  rowsPerPageState,
  setRowsPerPageState,
}) {
  const userColumns = [
    {
      header: "Email",
      accessor: "email",
      headerClassName: "w-56 text-start",
      render: (element) => {
        const maskEmail = (email) => {
          if (typeof email !== "string" || !email.includes("@")) {
            return email || "- - - - - ";
          }

          const [user, domain] = email.split("@");

          if (!user || user.length <= 4) return email;

          const maskedUser =
            user.slice(0, 2) + "*".repeat(user.length - 4) + user.slice(-2);

          return `${maskedUser}@${domain}`;
        };

        return <div className="w-48">{maskEmail(element)}</div>;
      },
    },
    {
      header: "Mobile",
      accessor: "mobile",
      headerClassName: "w-24 text-start",
      render: (element) => {
        const maskMobile = (mobile) => {
          const mobileStr = String(mobile);
          if (mobileStr.length < 4) return mobileStr;
          return (
            mobileStr.slice(0, 2) +
            "*".repeat(mobileStr.length - 4) +
            mobileStr.slice(-2)
          );
        };

        return <div>{element ? maskMobile(element) : "- - - - - "}</div>;
      },
    },
    {
      header: "Medium",
      accessor: "notificationMedium",
      headerClassName: "w-36 text-center",
      render: (element) => (
        <div className="flex items-center justify-center gap-4">
          {element && element.length > 0 ? (
            element.split(", ").map((item, index) => (
              <div key={index} className="flex">
                {item === "in-app" && (
                  <RiComputerLine className="text-xl text-[#66AFFF]" />
                )}

                {item === "email" && (
                  <MdOutlineEmail className="text-xl text-[#66AFFF]" />
                )}

                {item === "sms" && (
                  <MdOutlineSms className="text-xl text-[#66AFFF]" />
                )}
              </div>
            ))
          ) : (
            <span className="text-gray-400">- - - - -</span>
          )}
        </div>
      ),
    },

    {
      header: "Click Status",
      accessor: "clickStatus",
      headerClassName: "w-24",
      render: (element) => (
        <div className="flex items-center justify-center ">
          {element == 0 ? (
            <RxCross2 size={20} className="text-red-600" />
          ) : (
            <MdDone size={25} className="text-green-600" />
          )}
        </div>
      ),
    },
    {
      header: "Read Status",
      accessor: "readStatus",
      headerClassName: "w-24",
      render: (element) => (
        <div className="flex items-center justify-center">
          {element === false ? (
            <RxCross2 size={20} className="text-red-600" />
          ) : (
            <MdDone size={25} className="text-green-600" />
          )}
        </div>
      ),
    },
    {
      header: "Created At",
      accessor: "createdAt",
      headerClassName: "w-48",
      render: (element) => (
        <div className="flex items-center justify-center">
          {element ? (
            <DateTimeFormatter
              className="flex flex-row gap-2  "
              timeClass=""
              dateTime={element}
            />
          ) : (
            <span className="text-gray-400">- - - - - </span>
          )}
        </div>
      ),
    },
    {
      header: "Sent At",
      accessor: "sentAt",
      headerClassName: "w-48",
      render: (element) => (
        <div className="flex items-center justify-center">
          {element ? (
            <DateTimeFormatter
              className="flex flex-row gap-2   "
              timeClass=""
              dateTime={element}
            />
          ) : (
            <span className="text-gray-400 ">- - - - - </span>
          )}
        </div>
      ),
    },
    {
      header: "Consent Status",
      accessor: "status",
      headerClassName: "text-right  pr-6",
      tableDataClassName: "w-28  ",
      render: (element) => (
        <div className="flex justify-center items-center">
          <Tag
            label={element}
            variant={
              element === "sent"
                ? "active"
                : element === "error"
                ? "inactive"
                : "suspended"
            }
            className="font-sans text-xs font-medium capitalize w-24"
          />
        </div>
      ),
    },
  ];

  return (
    <div className="">
      {tableDataRows.length === 0 && !loading ? (
        <NoDataFound height="200px" />
      ) : (
        <div className="mt-4">
          <DataTable
            columns={userColumns}
            data={tableDataRows}
            hasSerialNumber={true}
            totalPages={totalPages}
            currentPage={currentPage}
            setCurrentPage={setCurrentPage}
            rowsPerPageState={rowsPerPageState}
            tableHeight={"230px"}
            setRowsPerPageState={setRowsPerPageState}
            searchable={false}
            loading={loading}
          />
        </div>
      )}
    </div>
  );
}

export default ConsentMain;
