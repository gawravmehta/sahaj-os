"use client";
import DataTable from "@/components/shared/data-table/DataTable";
import Button from "@/components/ui/Button";
import Header from "@/components/ui/Header";
import Tag from "@/components/ui/Tag";
import { usePermissions } from "@/contexts/PermissionContext";
import { apiCall } from "@/hooks/apiCall";
import { getErrorMessage } from "@/utils/errorHandler";
import { getLanguageLabel } from "@/utils/helperFunctions";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import toast from "react-hot-toast";
import { FiPlus } from "react-icons/fi";
import { MdOutlineModeEdit } from "react-icons/md";

const Page = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState("");
  const [collectionPoint, setCollectionPoint] = useState([]);
  const [rowsPerPageState, setRowsPerPageState] = useState(20);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");

  const { canWrite } = usePermissions();

  const router = useRouter();
  useEffect(() => {
    getCollectionPoint();
  }, [rowsPerPageState, currentPage, debouncedSearch]);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedSearch(search);
    }, 500);

    return () => {
      clearTimeout(handler);
    };
  }, [search]);

  const getCollectionPoint = async () => {
    setLoading(true);
    try {
      let url = `/cp/get-all-cps?current_page=${currentPage}&data_per_page=${rowsPerPageState}`;

      if (debouncedSearch) {
        url += `&search_query=${encodeURIComponent(debouncedSearch)}`;
      }

      const response = await apiCall(url);
      setCollectionPoint(response.collection_points);
      setCurrentPage(response.current_page);
      setTotalPages(response.total_pages);
      setLoading(false);
    } catch (error) {
      toast.error(getErrorMessage(error));
      setLoading(false);
    }
  };

  const userColumns = [
    {
      header: "Name",
      accessor: "cp_name",
      headerClassName: "text-left w-60",
      render: (element) => {
        return (
          <>
            {element ? (
              <div className="text-ellipsis">{element}</div>
            ) : (
              <div className="">- - - -</div>
            )}
          </>
        );
      },
    },
    {
      header: "Description",
      accessor: "cp_description",
      headerClassName: "text-left",
      render: (element, row) => {
        return (
          <>
            {element ? (
              <div className="line-clamp-2 w-96 text-ellipsis">{element}</div>
            ) : (
              <div className="">- - - - -</div>
            )}
          </>
        );
      },
    },

    {
      header: "Data Elements",
      accessor: "data_elements",
      headerClassName: "text-left ",
      render: (element) => {
        return (
          <div className="flex capitalize">
            {element?.slice(0, 1).map((item, index) => (
              <Tag key={index} variant="outlineBlue" label={item?.de_name} />
            ))}
          </div>
        );
      },
    },

    {
      header: "Language",
      accessor: "default_language",
      headerClassName: "text-center ",
      render: (element) => {
        return (
          <p className="text-center capitalize">{getLanguageLabel(element)}</p>
        );
      },
    },

    {
      header: "Status",
      accessor: "cp_status",
      headerClassName: "text-center",
      render: (element) => (
        <Tag
          variant={
            element == "published"
              ? "active"
              : element == "archived"
              ? "inactive"
              : "draft"
          }
          label={element}
          className="mx-auto w-24 capitalize"
        />
      ),
    },

    {
      header: "",
      accessor: "cp_id",
      headerClassName: " text-center  ",
      render: (element, row) => {
        return (
          row?.cp_status == "draft" && (
            <Button
              variant="icon"
              onClick={(e) => {
                e.stopPropagation();
                router.push(`/apps/collection-point/${element}?type=edit`);
              }}
              disabled={!canWrite("/apps/collection-point")}
              className={"px-6"}
            >
              <MdOutlineModeEdit size={16} />
            </Button>
          )
        );
      },
    },
  ];

  return (
    <>
      <div className="flex justify-between border-b border-borderheader">
        <Header
          title="Collection Point"
          subtitle="Points where you will show notice and gather personal data"
        />

        <div className="flex items-center justify-center gap-2 pr-6">
          <Button
            onClick={() =>
              router.push("/apps/collection-point/create-collection-point")
            }
            variant="secondary"
            disabled={!canWrite("/apps/collection-point")}
            className="hover:none gap-1"
          >
            <FiPlus size={18} />
            Collection Point
          </Button>
        </div>
      </div>

      <DataTable
        tableHeight={"213px"}
        columns={userColumns}
        data={collectionPoint}
        loading={loading}
        totalPages={totalPages}
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
        rowsPerPageState={rowsPerPageState}
        setRowsPerPageState={setRowsPerPageState}
        getRowRoute={(row) =>
          row?.cp_id ? `/apps/collection-point/details/${row?.cp_id}` : null
        }
        illustrationText="No Collection Point Available"
        illustrationImage="/assets/illustrations/no-data-find.png"
        noDataText="No Collection Point Found"
        noDataImage="/assets/illustrations/no-data-find.png"
      />
    </>
  );
};

export default Page;
