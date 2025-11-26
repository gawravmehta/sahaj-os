"use client";
import Button from "@/components/ui/Button";
import Skeleton from "@/components/ui/Skeleton";
import { usePermissions } from "@/contexts/PermissionContext";
import { apiCall } from "@/hooks/apiCall";
import { useDebounce } from "@/hooks/useDebounce";
import { getErrorMessage } from "@/utils/errorHandler";
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import toast from "react-hot-toast";
import { FaArrowRight } from "react-icons/fa6";
import { FiSearch } from "react-icons/fi";
import { IoClose } from "react-icons/io5";
import { LuCopy } from "react-icons/lu";
import { MdAdd, MdClear, MdDone, MdOutlineArrowBack } from "react-icons/md";
import { RxCross2 } from "react-icons/rx";

const AddDataElement = ({ setVisible, getAllDataElement, setDeData }) => {
  const router = useRouter();
  const [apiData, setApiData] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [isFetchMoreLoading, setIsFetchMoreLoading] = useState(false);
  const [searchPurpose, setSearchPurpose] = useState("");
  const debouncedSearchPurpose = useDebounce(searchPurpose, 500);
  const [purposeDetails, setPurposeDetails] = useState("");
  const [copyLoading, setCopyLoading] = useState(false);

  const { canWrite } = usePermissions();

  useEffect(() => {
    fetchData(page);
  }, [page]);

  useEffect(() => {
    setPage(1);
    setApiData([]);
    fetchData(1);
  }, [debouncedSearchPurpose]);

  const loaderRef = useRef();

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore && !loading) {
          setPage((prevPage) => prevPage + 1);
        }
      },
      { threshold: 1.0 }
    );

    if (loaderRef.current) {
      observer.observe(loaderRef.current);
    }

    return () => {
      if (loaderRef.current) {
        observer.unobserve(loaderRef.current);
      }
    };
  }, [hasMore, loading]);

  const fetchData = async (currentPage) => {
    if (currentPage === 1) {
      setLoading(true);
    } else {
      setIsFetchMoreLoading(true);
    }
    try {
      const response = await apiCall(`/data-elements/templates`, {
        params: {
          current_page: currentPage,
          data_per_page: 20,
          search_query: searchPurpose,
        },
      });

      const newData = response?.data_elements || [];

      setApiData((prev) => [...prev, ...newData]);
      setHasMore(newData.length === 20);
    } catch (error) {
      toast.error(getErrorMessage(error));
      console.error("Error fetching data:", error?.response || error.message);
      if (currentPage === 1) setApiData([]);
    } finally {
      if (currentPage === 1) {
        setLoading(false);
      } else {
        setIsFetchMoreLoading(false);
      }
    }
  };

  const handleBusinessProcessClick = (elementName) => {
    router.push(
      `/apps/purpose-management/consent-directory?query=${encodeURIComponent(
        elementName
      )}`
    );
  };

  const handleCreateCopy = async (e, data = null) => {
    if (e) e.preventDefault();

    setCopyLoading(true);

    const selectedData = data || purposeDetails;

    if (!selectedData?.id) {
      toast.error("No data element selected");
      setCopyLoading(false);
      return;
    }

    try {
      const response = await apiCall(
        `/data-elements/copy-data-element?de_id=${selectedData.id}`,
        {
          method: "POST",
        }
      );

      if (response) {
        toast.success("Data element copied successfully");
        setVisible(true);
        getAllDataElement();
        setDeData((prev) => [...prev, response]);

        setShowModal(false);
      }
    } catch (error) {
      toast.error(getErrorMessage(error));
      console.error("Error creating copy:", error);
    } finally {
      setCopyLoading(false);
    }
  };

  return (
    <>
      <div className="flex flex-col">
        <div>
          <div className="fixed right-0 top-[125.5px] h-[calc(100vh-60px)] w-[40%] border-l border-borderheader bg-[#F9FCFF] py-3 md:w-[30%] lg:w-[25%] xl:w-[20%]">
            {!purposeDetails ? (
              <>
                <div className="flex justify-between px-3.5 ">
                  <p className="">Explore Data Veda</p>

                  <IoClose
                    size={25}
                    className="cursor-pointer text-red-500"
                    onClick={() => {
                      setVisible(true);
                      setSearchPurpose("");
                      setPurposeDetails("");
                      setApiData([]);
                      setPage(1);
                    }}
                  />
                </div>
                <div className="my-2 border-b border-borderheader"></div>
                <div className="custom-scrollbar h-[calc(100vh-140px)] mt-2 overflow-y-auto pb-12">
                  {loading ? (
                    Array(10)
                      .fill(null)
                      .map((_, index) => (
                        <div
                          key={index}
                          className="border-b border-[#D6D6D6] px-3.5 py-3"
                        >
                          <Skeleton variant="multiple" className="w-full" />
                        </div>
                      ))
                  ) : apiData.length > 0 ? (
                    <div className="mb-10">
                      {apiData.map((data, index) => (
                        <div
                          key={index}
                          className="flex items-center justify-between border-b border-[#D6D6D6] px-3.5 py-3 hover:bg-[#f2f9ff] cursor-pointer"
                        >
                          <div className="relative flex w-full flex-col">
                            <div className="flex">
                              <div
                                className="w-[90%]"
                                onClick={() => setPurposeDetails(data)}
                              >
                                <h1 className="mb-1 max-w-52 cursor-pointer truncate text-sm text-black">
                                  {data.title}
                                </h1>
                                <p className="line-clamp-3 text-xs text-subHeading">
                                  {data.description}
                                </p>
                              </div>
                              <Button
                                variant="icon"
                                disabled={!canWrite("/apps/data-element")}
                                onClick={() => setShowModal(data)}
                                className="absolute right-0 cursor-pointer rounded-full bg-primary p-0.5 text-white"
                              >
                                <MdAdd />
                              </Button>
                            </div>
                          </div>
                        </div>
                      ))}

                      {isFetchMoreLoading && (
                        <p className="py-2 text-center text-sm">Loading...</p>
                      )}
                      <div ref={loaderRef} className="h-1" />
                    </div>
                  ) : searchPurpose.length > 0 ? (
                    <p className="mt-4 px-3.5 text-center text-sm text-gray-500">
                      No results found
                    </p>
                  ) : (
                    ""
                  )}
                </div>
              </>
            ) : (
              <div className=" h-[calc(100vh-180px)]  -mt-3">
                <>
                  <div className=" flex justify-between px-3.5 pt-2 border-b border-borderheader pb-3">
                    <p className="text-lg font-medium">Details</p>

                    <IoClose
                      size={25}
                      className="cursor-pointer text-red-500"
                      onClick={() => {
                        setVisible(true);
                        setSearchPurpose("");
                        setPurposeDetails("");
                        setApiData([]);
                        setPage(1);
                      }}
                    />
                  </div>
                </>
                <div className="h-[calc(100vh-270px)] custom-scrollbar overflow-y-auto  pb-2 pt-3">
                  <div className="px-3.5">
                    <h1 className="text-sm text-black">
                      {purposeDetails.title}
                    </h1>
                    <p className="mt-2 text-xs text-gray-600">
                      {purposeDetails.description}
                    </p>
                  </div>

                  <p className="mt-3.5 flex flex-col text-xs capitalize text-gray-600 px-3.5">
                    <span className="text-sm text-black pb-2">Alias</span>{" "}
                    {purposeDetails?.aliases &&
                    purposeDetails.aliases.length > 0 &&
                    !purposeDetails.aliases.every(
                      (name) => name.toLowerCase() === "black"
                    ) ? (
                      purposeDetails.aliases
                        .map((name) => name.replace(/_/g, " "))
                        .join(", ")
                    ) : (
                      <span className="text-gray-400">N/A</span>
                    )}
                  </p>
                  <p className="mt-3.5 flex flex-col text-xs text-gray-600 px-3.5">
                    <span className="text-sm text-black pb-2">Domain</span>{" "}
                    <p>
                      {purposeDetails?.domain ? (
                        <span>{purposeDetails.domain}</span>
                      ) : (
                        <span className="text-gray-400">N/A</span>
                      )}
                    </p>
                  </p>

                  <div className="fixed bottom-14 flex w-[40%] md:w-[30%] lg:w-[25%] xl:w-[20%] px-3.5 border-t flex-col items-center justify-center bg-[#F9FCFF] ">
                    <div className="mt-3 flex w-full flex-col  justify-between bg-[#F9FCFF]">
                      <Button
                        variant="secondary"
                        className="h-8 w-full "
                        onClick={() =>
                          handleBusinessProcessClick(purposeDetails.title)
                        }
                      >
                        <span className="flex gap-3 items-center">
                          <Image
                            alt="purpose-management"
                            src="/assets/apps-icons/purpose-management.png"
                            height={100}
                            width={100}
                            className="h-6 w-6"
                          />
                          <span>Consent Directory</span> <FaArrowRight />
                        </span>
                      </Button>
                    </div>

                    <div className="fixed bottom-0 flex w-[40%] md:w-[30%] lg:w-[25%] xl:w-[20%] items-center justify-around gap-24 border-t  border-borderheader bg-[#F9FCFF] py-1">
                      <Button
                        variant="back"
                        onClick={() => {
                          setPurposeDetails("");
                          setSearchPurpose("");
                          setPage(1);
                          setApiData([]);
                          setHasMore(true);
                          fetchData(1);
                        }}
                      >
                        <MdOutlineArrowBack size={16} /> Back
                      </Button>
                      <Button
                        variant="primary"
                        onClick={() => setShowModal(purposeDetails)}
                        disabled={
                          copyLoading || !canWrite("/apps/data-element")
                        }
                        className={`px-6 text-sm ${
                          copyLoading ? "cursor-not-allowed opacity-60" : ""
                        }`}
                      >
                        <LuCopy className="mr-1" />
                        {copyLoading ? "Processing..." : "Copy"}
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      {showModal && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-[#f2f9ff]/70 "
          onClick={() => setShowModal(false)}
        >
          <div className="flex h-full w-full items-center justify-center">
            <div className="h-[250px] bg-white p-5 border border-[#c7cfe2]">
              <div className="flex items-center justify-end gap-1 p-1">
                <RxCross2
                  size={24}
                  className="cursor-pointer text-red-500"
                  onClick={() => setShowModal(false)}
                />
              </div>
              <div className="m-auto flex w-[80%] flex-col items-center justify-center text-center">
                <p>
                  Do you want to create a copy of this Data Element in your
                  workplace?
                </p>
                <div className="mt-4 flex w-full items-center justify-center gap-4 py-5">
                  <Button
                    variant="no"
                    onClick={() => setShowModal(false)}
                    className="h-8 border border-[#c7cfe2] px-8 py-2 text-sm"
                  >
                    NO
                  </Button>
                  <Button
                    variant="primary"
                    onClick={(e) => handleCreateCopy(e, showModal)}
                    className="h-8 bg-primary px-8 py-2 text-sm text-white"
                  >
                    Yes
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default AddDataElement;
