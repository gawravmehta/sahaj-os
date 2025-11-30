"use client";

import { useRouter } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { FaLongArrowAltDown, FaLongArrowAltUp } from "react-icons/fa";
import { LuCheck } from "react-icons/lu";
import { RxCross2 } from "react-icons/rx";

import Image from "next/image";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import toast from "react-hot-toast";
import Tag from "@/components/ui/Tag";
import DateTimeFormatter from "@/components/ui/DateTimeFormatter";
import Header from "@/components/ui/Header";
import Button from "@/components/ui/Button";
import { InputField, SelectInput } from "@/components/ui/Inputs";
import Skeleton from "@/components/ui/Skeleton";
import DataTable from "@/components/shared/data-table/DataTable";
import Link from "next/link";
import { usePermissions } from "@/contexts/PermissionContext";

const Page = () => {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [statusLoading, setStatusLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [rowsPerPageState, setRowsPerPageState] = useState(10);
  const [totalPages, setTotalPages] = useState(1);
  const [sortOrder, setSortOrder] = useState("desc");

  const [verificationModalOpen, setVerificationModalOpen] = useState(false);

  const [verificationRequests, setVerificationRequests] = useState([]);

  const [isConsentGivenModal, setIsConsentGivenModal] = useState(false);

  const [dpId, setDpId] = useState("");
  const [dpSystemId, setDpSystemId] = useState("");

  const [currentDataElements, setCurrentDataElements] = useState([]);

  const [purposeOptions, setPurposeOptions] = useState([]);
  const [currentPurpose, setCurrentPurpose] = useState(null);
  const [deOption, setDeOptions] = useState([]);
  const [currentDe, setCurrentDe] = useState(null);
  const [isVerified, setIsVerified] = useState(false);

  const [dpEmail, setDpEmail] = useState("");
  const [dpMobile, setDpMobile] = useState("");

  const [identifierType, setIdentifierType] = useState("dp_id");
  const [identifierValue, setIdentifierValue] = useState("");
  const [status, setStatus] = useState({});
  const [missingFields, setMissingFields] = useState([]);

  const { canWrite } = usePermissions();

  const identifierOptions = [
    { label: "Data Principal ID", value: "dp_id" },
    { label: "Data Principal System ID", value: "dp_system_id" },
    { label: "Data Principal Email", value: "dp_e" },
    { label: "Data Principal Mobile", value: "dp_m" },
  ];

  const [filterOption, setFilterOption] = useState({});
  const [currentAppliedFilters, setCurrentAppliedFilters] = useState({});
  const [searchQuery, setSearchQuery] = useState("");
  const handleSearch = (query) => {
    setSearchQuery(query);
    setCurrentPage(1);
  };

  useEffect(() => {
    fetchPurposes();
    fetchDataElement();
    fetchStatus();
  }, []);

  const fetchPurposes = async () => {
    try {
      const purposes = await apiCall(`/purposes/get-all-purposes`);

      const formattedPurposes = purposes.purposes
        .filter(
          (purpose) =>
            purpose.purpose_status === "published" || purpose.is_published
        )
        .map((purpose) => ({
          value: purpose.purpose_hash_id,
          label: purpose.purpose_title,
        }));

      setPurposeOptions(formattedPurposes);
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      console.error("Error in fetchPurposes:", errorMessage);
      toast.error(errorMessage || "Failed to fetch purposes");
    }
  };
  const fetchDataElement = async () => {
    try {
      const response = await apiCall(`/data-elements/get-all-data-element`);

      const formattedDE = response.data_elements
        .filter((item) => item.de_status === "published" || item.is_published)
        .map((item) => ({
          value: item.de_hash_id,
          label: item.de_name,
        }));

      setDeOptions(formattedDE);
    } catch (error) {
      const errorMessage = getErrorMessage(error);

      toast.error(errorMessage || "Failed to fetch purposes");
    }
  };

  const fetchStatus = async () => {
    setStatusLoading(true);
    try {
      const res = await apiCall(
        "/consent-validation/verification-dashboard-stats"
      );
      setStatus(res);
      setStatusLoading(false);
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      toast.error(errorMessage || "Failed to fetch purposes");
      setStatusLoading(false);
    }
  };

  const handleApplyFilters = (selectedFilters) => {
    setLoading(true);
    setCurrentPage(1);
    setCurrentAppliedFilters(selectedFilters);
    getAuditLogs(selectedFilters);
  };

  const getAuditLogs = async (filters) => {
    setLoading(true);
    const page = currentPage === 0 ? 1 : currentPage;

    const {
      purpose_titles,
      data_element_titles,
      internal_external,
      status,
      start_date,
      end_date,
    } = filters || {};

    const queryParams = new URLSearchParams({
      page: page,
      limit: rowsPerPageState,
      sort_order: sortOrder,
      search: searchQuery,
    });

    const appendIfNotEmpty = (key, value) => {
      if (Array.isArray(value) && value.length > 0) {
        queryParams.append(key, value.join(","));
      } else if (!Array.isArray(value) && value) {
        queryParams.append(key, value);
      }
    };

    appendIfNotEmpty("purpose_titles", purpose_titles);
    appendIfNotEmpty("data_element_titles", data_element_titles);
    appendIfNotEmpty("internal_external", internal_external);
    appendIfNotEmpty("status", status);

    if (start_date) queryParams.append("from_date", start_date);
    if (end_date) queryParams.append("to_date", end_date);

    try {
      const response = await apiCall(
        `/consent-validation/get-all-verification-logs?page=1&limit=10${queryParams.toString()}`
      );

      setVerificationRequests(response.logs_data);
      setTotalPages(response.total_pages);
      setFilterOption(response.filter_options);
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      toast.error(errorMessage || "Failed to fetch purposes");
    } finally {
      setLoading(false);
    }
  };

  const handleSortChange = () => {
    const newSortOrder = sortOrder === "asc" ? "desc" : "asc";
    setSortOrder(newSortOrder);
    setCurrentPage(1);
  };

  useEffect(() => {
    getAuditLogs();
  }, [rowsPerPageState, currentPage, sortOrder, searchQuery]);
  const validateForm = () => {
    const newMissingFields = [];

    if (!identifierType || !identifierType.value) {
      newMissingFields.push("identifier");
    }

    if (!identifierValue.trim()) {
      newMissingFields.push("identifier_value");
    }

    if (!currentPurpose) {
      newMissingFields.push("purpose");
    }

    if (!currentDe || currentDe.length === 0) {
      newMissingFields.push("data-element");
    }

    setMissingFields(newMissingFields);
    return newMissingFields.length === 0;
  };

  const handleVerificationRequest = async () => {
    if (!validateForm()) {
      toast.error("Please fill all required fields");
      return;
    }
    try {
      const payload = {
        [identifierType.value]: identifierValue,
        purpose_hash: currentPurpose?.value,
        data_elements_hash: currentDe.map((item) => item.value),
      };

      const response = await apiCall(
        "/consent-validation/verify-consent-internal",
        {
          method: "POST",
          data: payload,
        }
      );

      if (response) {
        if (response.verified == true) {
          setIsVerified(true);
          setIsConsentGivenModal(true);
        } else {
          setIsConsentGivenModal(true);
        }

        setVerificationModalOpen(false);
        setDpId("");
        setDpSystemId("");
        setDpMobile("");
        setDpEmail("");
        setCurrentDataElements([]);
        setCurrentPurpose(null);
        setCurrentDe(null);
        setIdentifierValue("");
        setMissingFields([]);
        getAuditLogs();
      }
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      toast.error(errorMessage || "Verification request failed");
    }
  };
  useEffect(() => {
    if (verificationModalOpen) {
      setMissingFields([]);
    }
  }, [verificationModalOpen]);

  const auditLog = [
    {
      header: "Request ID",
      accessor: "request_id",
      headerClassName: "w-42 px-4 text-left",
      render: (element) => (
        <div className="flex px-4">
          <div className="max-w-28 truncate text-ellipsis py-1.5">
            {element}
          </div>
        </div>
      ),
    },
    {
      header: "Scope",
      accessor: "scope",
      headerClassName: " text-left",
      render: (element) => (
        <div className="py-2">
          <p className="max-w-48 truncate pb-2">
            {element.data_element_hashes}
          </p>
          <p className="max-w-48 truncate pb-2">{element.purpose_hash}</p>
        </div>
      ),
    },

    {
      header: "DP ID",
      accessor: "dp_id",
      headerClassName: "w-42 px-4 text-left",
      render: (element) => (
        <div className="flex px-4">
          <div className="max-w-24 truncate text-ellipsis py-1.5">
            {element}
          </div>
        </div>
      ),
    },

    {
      header: "Origin",
      accessor: "internal_external",
      headerClassName: " px-4  text-left",

      render: (element) => (
        <div className="truncate text-ellipsis px-4">{element}</div>
      ),
    },

    {
      header: "Verifyed By",
      accessor: "ver_requested_by",
      headerClassName: " px-4 text-left",
      render: (element) => (
        <div className="flex max-w-64 gap-1 truncate text-ellipsis px-5">
          <span>{element}</span>
        </div>
      ),
    },

    {
      header: "Consent Status",
      accessor: "consent_status",
      headerClassName: " max-w-28 px-3 text-left",
      render: (element) => (
        <div className="max-w-24 px-3 ">
          {element ? (
            <Tag
              variant="active"
              label={"Granted"}
              className="mx-auto w-24 capitalize"
            />
          ) : (
            <Tag
              variant="inactive"
              label={"Denied"}
              className="mx-auto w-24 capitalize"
            />
          )}
        </div>
      ),
    },
    {
      header: "Req. Status",
      accessor: "status",
      headerClassName: " max-w-20 px-3 text-left",
      render: (element) => (
        <div className="flex max-w-20 items-center justify-center px-3">
          {element === "successful" ? (
            <LuCheck className="size-5 text-[#28A745]" />
          ) : (
            <RxCross2 className="size-5 text-[#FE4343]" />
          )}
        </div>
      ),
    },
    {
      header: (
        <div
          className="flex cursor-pointer items-center gap-1"
          onClick={() => handleSortChange()}
        >
          <span>Timestamp</span>
          {sortOrder === "asc" ? <FaLongArrowAltUp /> : <FaLongArrowAltDown />}
        </div>
      ),
      accessor: "timestamp",
      headerClassName: "px-3 text-left",
      render: (element) => (
        <div className="text-left">
          {" "}
          <DateTimeFormatter className="text-xs" dateTime={element} />
        </div>
      ),
    },
  ];

  const clearFilter = () => {
    const resetFilters = {};
    filterDetails.forEach((item) => {
      resetFilters[item.name] = item.isMultiSelect ? [] : null;
    });
    getAuditLogs(resetFilters);
  };

  const handleDownloadCSV = async () => {
    setLoading(true);

    const page = currentPage === 0 ? 1 : currentPage;

    const {
      purpose_titles = [],
      data_element_titles = [],
      internal_external = [],
      status = [],
      start_date,
      end_date,
    } = currentAppliedFilters || {};

    const queryParams = new URLSearchParams({
      page: page.toString(),
      limit: rowsPerPageState.toString(),
      sort_order: sortOrder,
      search: searchQuery,
    });

    if (!searchQuery) {
      queryParams.delete("search");
    }

    const appendFilterValues = (key, value) => {
      if (Array.isArray(value)) {
        value.forEach((item) => queryParams.append(key, item));
      } else if (value) {
        queryParams.append(key, value);
      }
    };

    appendFilterValues("purpose_titles", purpose_titles);
    appendFilterValues("data_element_titles", data_element_titles);
    appendFilterValues("internal_external", internal_external);
    appendFilterValues("status", status);

    if (start_date) queryParams.append("from_date", start_date);
    if (end_date) queryParams.append("to_date", end_date);

    try {
      const response = await apiCall(
        `/consent-validation/download-verification-logs?${queryParams.toString()}`
      );

      const respText = await response;

      const blob = new Blob([respText], { type: "text/csv" });
      const downloadUrl = window.URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = downloadUrl;
      a.download = "verification_logs.csv";
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(downloadUrl);
    } catch (error) {
      console.error("CSV Download Error:", error);
      toast.error("Error downloading CSV");
    } finally {
      setLoading(false);
    }
  };
  const filterDetails = [
    {
      name: "internal_external",
      label: "Origin",
      options: filterOption?.internal_external?.map((item) => ({
        value: item,
        label: item,
      })),
    },
    {
      name: "status",
      label: "Status",
      options: filterOption?.status?.map((item) => ({
        value: item,
        label: item,
      })),
    },
    {
      name: "purpose_titles",
      label: "Purposes",
      options: filterOption?.purpose_titles?.map((item) => ({
        value: item,
        label: item,
      })),
      isMultiSelect: true,
    },
    {
      name: "data_element_titles",
      label: "Data Elements",
      options: filterOption?.data_element_titles?.map((item) => ({
        value: item,
        label: item,
      })),
      isMultiSelect: true,
    },
  ];

  function formatCompactNumber(value) {
    if (value === null || value === undefined || value === "")
      return <h1 className="text-xl text-primary">N/A</h1>;

    const number = Number(value);
    if (isNaN(number)) return value;

    if (number < 1000) return number.toString();

    return (number / 1000).toFixed(1).replace(/\.0$/, "") + "K";
  }

  return (
    <div className="h-full text-gray-800">
      <div className="flex items-center justify-between border-b border-borderheader pr-6">
        <Header
          title="Consent Validation"
          subtitle="Manage your consent validation requests and view statistics"
        />
        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            onClick={() => {
              setVerificationModalOpen(true);
            }}
            disabled={!canWrite("/apps/consent-validation")}
          >
            Manual Validation
          </Button>

          <Link href="/apps/consent-validation/bulk-verification">
            <Button
              variant="secondary"
              onClick={() => {
                router.push("/apps/consent-validation/bulk-verification");
              }}
              disabled={!canWrite("/apps/consent-validation")}
            >
              Bulk Validation
            </Button>
          </Link>
        </div>
        {verificationModalOpen && (
          <div
            onClick={() => {
              setVerificationModalOpen(false);
            }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-[#f2f9ff]/50"
          >
            <div
              onClick={(e) => e.stopPropagation()}
              className="flex w-[444px] flex-col justify-between border border-[#c7cfe2] bg-white"
            >
              <div className="px-10 py-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold">
                    Manual Verification Request
                  </h2>
                  <RxCross2
                    onClick={() => setVerificationModalOpen(false)}
                    size={20}
                    className="cursor-pointer font-semibold text-[#d94e4e]"
                  />
                </div>
                <p className="mb-4 mt-2 text-sm text-gray-400">
                  Please provide the necessary details to verify your request.
                </p>
                <div className="space-y-4">
                  <SelectInput
                    name="identifier"
                    label="Identifier"
                    options={identifierOptions}
                    value={identifierType}
                    onChange={setIdentifierType}
                    placeholder="Select Identifier"
                    required
                    missingFields={missingFields}
                    tooltipText="Choose the unique field  that will be used to identify the individual."
                  />
                  <InputField
                    name="identifier_value"
                    label="Identifier Value"
                    placeholder="Enter Identifier Value"
                    value={identifierValue}
                    onChange={(e) => setIdentifierValue(e.target.value)}
                    required
                    missingFields={missingFields}
                    tooltipText="Provide the actual value for the selected identifier."
                  />

                  <SelectInput
                    name="purpose"
                    label="Purpose"
                    options={purposeOptions}
                    value={currentPurpose}
                    onChange={setCurrentPurpose}
                    placeholder="Select Purpose"
                    tooltipText="Select a purpose associated with the selected data element."
                    required
                    missingFields={missingFields}
                  />

                  {currentPurpose && (
                    <InputField
                      name="purpose_hash_id"
                      label="Purpose Hash ID"
                      placeholder="Purpose ID will be auto-filled"
                      value={currentPurpose?.value || ""}
                      disabled={true}
                      className="cursor-not-allowed text-gray-400"
                      tooltipText="Purpose ID will be auto-filled based on the selected purpose."
                      required
                      missingFields={missingFields}
                    />
                  )}

                  <SelectInput
                    name="data-element"
                    label="Data Elements"
                    isMulti={true}
                    options={deOption}
                    value={currentDe}
                    onChange={setCurrentDe}
                    placeholder="Select Data Elements"
                    tooltipText="Select published data elements to associate with this collection point."
                    required
                    missingFields={missingFields}
                  />

                  {currentDe && currentDe.length > 0 && (
                    <InputField
                      name="de_hash_ids"
                      label="Data Element Hash IDs"
                      placeholder="Data Element Hash IDs will be auto-filled"
                      value={currentDe.map((item) => item.value).join(", ")}
                      disabled={true}
                      className="cursor-not-allowed text-gray-400"
                      tooltipText="Data Element Hash IDs will be auto-filled based on the selected data elements."
                      required
                      missingFields={missingFields}
                    />
                  )}
                </div>
              </div>
              <div className="mt-3 flex justify-end gap-3 border-t border-borderPrimary px-10 py-2">
                <Button
                  variant="cancel"
                  onClick={() => {
                    setVerificationModalOpen(false);
                  }}
                >
                  Cancel
                </Button>

                <Button
                  variant="primary"
                  className="w-20"
                  onClick={handleVerificationRequest}
                >
                  Verify
                </Button>
              </div>
            </div>
          </div>
        )}
        {isConsentGivenModal && (
          <div
            onClick={() => {
              setIsConsentGivenModal(false);
            }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-[#f2f9ff]/50"
          >
            <div
              onClick={(e) => e.stopPropagation()}
              className="flex w-[500px] flex-col justify-between border border-[#c7cfe2] bg-white p-6"
            >
              <div>
                <Button variant="close" className="flex w-full justify-end">
                  <RxCross2
                    onClick={() => setIsConsentGivenModal(false)}
                    size={20}
                  />
                </Button>
                <div className="-mt-5">
                  <h2 className="text-xl font-semibold text-gray-800">
                    Consent Verification Result
                  </h2>
                  <p className="mt-3 text-sm text-gray-600">
                    The Data Principal has{" "}
                    <span
                      className={`font-medium ${
                        isVerified ? "text-green-600" : "text-red-600"
                      }`}
                    >
                      {isVerified ? "provided" : "not provided"}
                    </span>{" "}
                    consent for Data Elements for that Purpose.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className=" px-6 pt-4">
        <div className="grid grid-cols-2 gap-6">
          <div className="grid grid-cols-3 bg-white py-2 shadow">
            <div className="flex flex-col items-center justify-center gap-2 border-r-2 border-borderSecondary">
              <div className="size-16">
                <Image
                  src="/assets/varificationIcon/Data Processor (2).png"
                  height={1000}
                  width={1000}
                  quality={100}
                  className="h-full w-full object-contain text-amber-300"
                  alt="Notifications"
                />
              </div>
              <h3 className="text-base font-normal text-subText">
                Data Processors
              </h3>
              {!statusLoading ? (
                <div className="text-3xl font-medium text-primary">
                  {formatCompactNumber(status?.data_processors)}
                </div>
              ) : (
                <Skeleton variant="single" className={"h-4 w-20"} />
              )}
            </div>
            <div className="flex flex-col items-center justify-center gap-2 border-r-2 border-borderSecondary">
              <div className="size-16">
                <Image
                  src="/assets/varificationIcon/Request.png"
                  height={1000}
                  width={1000}
                  quality={100}
                  className="h-full w-full object-contain"
                  alt="Requests"
                />
              </div>
              <h3 className="text-base font-normal text-subText">Requests</h3>
              {!statusLoading ? (
                <div className="text-3xl font-medium text-primary">
                  {" "}
                  {formatCompactNumber(status?.total_requests)}
                </div>
              ) : (
                <Skeleton variant="single" className={"h-4 w-20"} />
              )}
            </div>
            <div className="flex flex-col items-center justify-center gap-2">
              <div className="size-16">
                <Image
                  src="/assets/varificationIcon/Notification.png"
                  height={1000}
                  width={1000}
                  quality={100}
                  className="h-full w-full object-contain"
                  alt="Notifications"
                />
              </div>
              <h3 className="text-base font-normal text-subText">
                Notifications
              </h3>
              {!statusLoading ? (
                <div className="text-3xl font-medium text-primary">
                  {" "}
                  {formatCompactNumber(status?.notification_count)}
                </div>
              ) : (
                <Skeleton variant="single" className={"h-4 w-20"} />
              )}
            </div>
          </div>
          <div className="space-y-3">
            <div className="grid grid-cols-2 bg-white py-4 shadow">
              <div className="border-r-2 border-borderSecondary pl-5">
                {" "}
                <h3 className="text-base font-normal text-subText">
                  Valid Results
                </h3>
                {!statusLoading ? (
                  <div className="text-2xl font-medium text-primary">
                    {" "}
                    {formatCompactNumber(status?.valid_results)}
                  </div>
                ) : (
                  <Skeleton variant="single" className={"h-4 w-20"} />
                )}
              </div>
              <div className="pl-5">
                {" "}
                <h3 className="text-base font-normal text-subText">
                  Invalid Results
                </h3>
                {!statusLoading ? (
                  <div className="text-2xl font-medium text-primary">
                    {" "}
                    {formatCompactNumber(status?.invalid_results)}
                  </div>
                ) : (
                  <Skeleton variant="single" className={"h-4 w-20"} />
                )}
              </div>
            </div>
            <div className="grid grid-cols-2 bg-white py-4 shadow">
              <div className="border-r-2 border-borderSecondary pl-5">
                {" "}
                <h3 className="text-base font-normal text-subText">Success</h3>
                {!statusLoading ? (
                  <div className="text-2xl font-medium text-primary">
                    {" "}
                    {status?.success_rate_percentage}%
                  </div>
                ) : (
                  <Skeleton variant="single" className={"h-4 w-20"} />
                )}
              </div>
              <div className="pl-5">
                {" "}
                <h3 className="text-base font-normal text-subText">Failed</h3>
                {!statusLoading ? (
                  <div className="text-2xl font-medium text-primary">
                    {" "}
                    {status?.failure_rate_percentage}%
                  </div>
                ) : (
                  <Skeleton variant="single" className={"h-4 w-20"} />
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className=" bg-white shadow mt-3">
        <DataTable
          loading={loading}
          hasFilterOption={true}
          tableHeight={"100px"}
          columns={auditLog}
          data={verificationRequests}
          totalPages={totalPages}
          currentPage={currentPage}
          rowsPerPageState={rowsPerPageState}
          setRowsPerPageState={setRowsPerPageState}
          setCurrentPage={setCurrentPage}
          filterWithDateRange={true}
          onApplyFilters={handleApplyFilters}
          clearFilter={clearFilter}
          isFilter={true}
          filterDetails={filterDetails}
          apiSearch={true}
          search={searchQuery}
          setSearch={setSearchQuery}
          onSearch={handleSearch}
          searchable={true}
          downloadCSV={true}
          getRowRoute={(row) =>
            row?._id ? `/apps/consent-validation/${row?.request_id}` : null
          }
          handleDownloadCSV={handleDownloadCSV}
        />
      </div>
    </div>
  );
};

export default Page;
