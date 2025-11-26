"use client";

import DataTable from "@/components/shared/data-table/DataTable";
import Button from "@/components/ui/Button";
import Header from "@/components/ui/Header";
import { SelectInput } from "@/components/ui/Inputs";
import Tag from "@/components/ui/Tag";
import { apiCall } from "@/hooks/apiCall";
import { useEffect, useState } from "react";
import { MdDone } from "react-icons/md";
import { RxCross2 } from "react-icons/rx";
import toast from "react-hot-toast";
import { getErrorMessage } from "@/utils/errorHandler";
import { getLanguageLabel } from "@/utils/helperFunctions";
import BulkDpDeleteModal from "@/components/features/principalManagement/BulkDpDeleteModal";

const Page = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [dpData, setDpData] = useState([]);
  const [rowsPerPageState, setRowsPerPageState] = useState(20);
  const [allTags, setAllTags] = useState([]);
  const [totalDP, setTotalDP] = useState([]);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedTags, setSelectedTags] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getAllTags();
  }, []);

  useEffect(() => {
    setTotalDP(null);
    getAllDataPrincipals();
  }, [currentPage, rowsPerPageState, selectedTags]);

  const getAllDataPrincipals = async () => {
    setLoading(true);
    try {
      const queryParams = new URLSearchParams();
      selectedTags.forEach((tag) => queryParams.append("dp_tags", tag));
      queryParams.append("page", currentPage);
      queryParams.append("limit", rowsPerPageState);

      const response = await apiCall(
        `/data-principal/get-all-data-principals?${queryParams.toString()}`
      );

      setDpData(response.dataPrincipals || []);
      setTotalPages(response.totalPages || 0);
      setTotalDP(response.totalPrincipals || 0);
    } catch (error) {
      toast.error(getErrorMessage(error));
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const getAllTags = async () => {
    try {
      const response = await apiCall("/data-principal/get-all-dp-tags");

      setAllTags(response.dp_tags || []);
    } catch (error) {
      toast.error(getErrorMessage(error));
      console.error(error);
    }
  };

  const closeModal = () => setShowDeleteModal(false);
  const tagOptions = allTags.map((tag) => ({
    label: tag.charAt(0).toUpperCase() + tag.slice(1),
    value: tag,
  }));

  const userColumns = [
    { header: "DP ID", accessor: "dp_id" },
    { header: "Email", accessor: "dp_email" },
    { header: "Mobile", accessor: "dp_mobile" },
    { header: "Country", accessor: "dp_country" },
    { header: "State", accessor: "dp_state" },
    {
      header: "Language",
      accessor: "dp_preferred_lang",
      render: (lang) => getLanguageLabel(lang),
    },
    {
      header: "Tags",
      accessor: "dp_tags",
      render: (tags) => {
        return (
          <div className="flex flex-wrap gap-1">
            {tags.map((t) => (
              <div>
                <Tag key={t} label={t} />
              </div>
            ))}
          </div>
        );
      },
    },
    {
      header: "Consent",
      accessor: "consent_count",
      render: (count) => {
        return (
          <div className="flex items-center justify-center">
            {count > 0 ? (
              <MdDone size={20} className="text-green-600" />
            ) : (
              <RxCross2 size={20} className="text-red-600" />
            )}
          </div>
        );
      },
    },
  ];

  return (
    <div className="flex">
      <div className="w-full">
        <div className="flex items-center justify-between border-b border-borderheader pb-2 pr-6">
          <Header
            title="Bulk Delete Data Principal"
            subtitle="Choose the relevant tags to delete bulk customer data"
          />

          <div className="flex items-center gap-4">
            {totalDP > 0 && selectedTags.length > 0 && (
              <Button onClick={() => setShowDeleteModal(true)} variant="delete">
                {`Delete ${totalDP} DP`}
              </Button>
            )}

            <SelectInput
              options={tagOptions}
              value={tagOptions.filter((option) =>
                selectedTags.includes(option.value)
              )}
              onChange={(selectedOptions) => {
                const values = selectedOptions
                  ? selectedOptions.map((opt) => opt.value)
                  : [];
                setSelectedTags(values);
                setCurrentPage(1);
              }}
              placeholder="Select Tags"
              isMulti
              className="w-64 text-sm"
            />
          </div>
        </div>

        <DataTable
          tableHeight="212px"
          columns={userColumns}
          data={dpData}
          totalPages={totalPages}
          currentPage={currentPage}
          setCurrentPage={setCurrentPage}
          rowsPerPageState={rowsPerPageState}
          setRowsPerPageState={setRowsPerPageState}
          loading={loading}
        />

        {showDeleteModal && (
          <BulkDpDeleteModal
            closeModal={closeModal}
            selectedTags={selectedTags}
            setSelectedTags={setSelectedTags}
            getAllDataPrincipals={getAllDataPrincipals}
          />
        )}
      </div>
    </div>
  );
};

export default Page;
