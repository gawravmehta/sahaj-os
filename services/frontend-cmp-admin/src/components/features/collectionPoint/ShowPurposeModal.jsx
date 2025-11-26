"use client";

import DataTable from "@/components/shared/data-table/DataTable";
import Button from "@/components/ui/Button";
import Link from "next/link";
import { useRouter } from "next/navigation";
import React, { useEffect, useState } from "react";
import { MdAdd } from "react-icons/md";
import { RxCross2 } from "react-icons/rx";

const ShowPurposeModal = ({
  selectedDeForPurpose,
  purposeOptions,
  totalPages,
  currentPage,
  setCurrentPage,
  rowsPerPageState,
  setRowsPerPageState,
  setShowPurposes,
  existingPurposes,
  formData,
  setFormData,
}) => {
  const [tempPurposes, setTempPurposes] = useState([]);

  const router = useRouter();

  useEffect(() => {
    if (Array.isArray(existingPurposes)) {
      setTempPurposes(existingPurposes);
    } else {
      setTempPurposes([]);
    }
  }, [existingPurposes]);

  const modalColumns = [
    {
      header: "Consent Purpose",
      accessor: "purpose_title",
      headerClassName: "pl-5",
      render: (element, row) => (
        <div className="w-96 flex flex-col py-3 pl-5 text-sm text-heading">
          <div>{element}</div>
          {row.data_processor_details.length > 0 && (
            <div className="flex items-center mt-1">
              <span className="text-xs text-gray-700">Data Processors:</span>
              {row.data_processor_details.map((detail, index) => (
                <Link
                  href={`/apps/vendors/details/${detail.data_processor_id}`}
                  target="_blank"
                  key={index}
                  className="text-[10px] text-gray-700 border px-2 mx-1 hover:cursor-pointer hover:bg-gray-100"
                >
                  {detail.data_processor_name}
                </Link>
              ))}
            </div>
          )}
        </div>
      ),
    },
    {
      accessor: "purpose_id",
      render: (element, row) => (
        <div className="flex items-end justify-end text-sm text-heading">
          <input
            type="checkbox"
            className="h-6 w-6 accent-primary"
            checked={tempPurposes?.some((p) => p.purpose_id === element)}
            onChange={() => {
              setTempPurposes((prev) => {
                const index = prev.findIndex((p) => p.purpose_id === element);
                if (index > -1) {
                  return prev.filter((p) => p.purpose_id !== element);
                } else {
                  return [
                    ...prev,
                    { purpose_id: element, purpose_title: row.purpose_title },
                  ];
                }
              });
            }}
          />
        </div>
      ),
    },
  ];

  const handleSelectPurposes = () => {
    if (!selectedDeForPurpose) return;

    const updatedDataElements = formData.data_elements.map((de) =>
      de.de_id === selectedDeForPurpose.value
        ? { ...de, purposes: tempPurposes }
        : de
    );

    setFormData({ ...formData, data_elements: updatedDataElements });
    setShowPurposes(false);
  };

  return (
    <div
      onClick={() => setShowPurposes(false)}
      className="fixed inset-0 z-50 flex items-center justify-center bg-[#f2f9ff]/50 bg-opacity-70"
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="relative w-full max-w-2xl border border-[#c7cfe2] bg-white p-6 pt-6"
      >
        <div className="absolute right-5 top-4">
          <Button variant="close" onClick={() => setShowPurposes(false)}>
            <RxCross2 size={20} />
          </Button>
        </div>

        <h2 className="mb-3 text-xl font-medium">
          Select Purposes for {selectedDeForPurpose?.label}
        </h2>

        <DataTable
          hasFilterOption
          columns={modalColumns}
          data={purposeOptions}
          searchable
          hasSerialNumber={false}
          totalPages={totalPages}
          currentPage={currentPage}
          setCurrentPage={setCurrentPage}
          rowsPerPageState={rowsPerPageState}
          setRowsPerPageState={setRowsPerPageState}
          tableWidth="290px"
          tableHeight="344px"
          hidePagination
        />

        <div className="flex items-center justify-end gap-2 px-2 pt-2">
          <Link href="/user/consent-governance/consent-gov/purpose-management/create">
            <Button variant="secondary" className="flex items-center gap-2">
              <MdAdd />
              <p>Create Purpose</p>
            </Button>
          </Link>

          <Button
            onClick={handleSelectPurposes}
            className="px-6"
            disabled={tempPurposes?.length === 0}
          >
            Select
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ShowPurposeModal;
