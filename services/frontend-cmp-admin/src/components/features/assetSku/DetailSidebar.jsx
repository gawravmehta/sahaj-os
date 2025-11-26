import { LuTrash } from "react-icons/lu";
import { RxCross2 } from "react-icons/rx";
import { BiPencil } from "react-icons/bi";
import { useRouter } from "next/navigation";
import { useState } from "react";
import Tag from "@/components/ui/Tag";
import Button from "@/components/ui/Button";
import DeleteModal from "@/components/shared/modals/DeleteModal";
import dayjs from "dayjs";
import toast from "react-hot-toast";
import { getErrorMessage } from "@/utils/errorHandler";
import { apiCall } from "@/hooks/apiCall";
import { usePermissions } from "@/contexts/PermissionContext";

const DetailSidebar = ({
  setHighlight,
  asset,
  setDetailBar,
  assets,
  setAssets,
}) => {
  const router = useRouter();
  const [openModal, setOpenModal] = useState(null);
  const [btnLoading, setBtnLoading] = useState(false);
  const { canWrite } = usePermissions();

  const closeModal = () => {
    setOpenModal(null);
  };

  const handlePublishAsset = async (id) => {
    setBtnLoading(true);
    try {
      const apiUrl = `/assets/publish-asset/${id}`;
      const response = await apiCall(apiUrl, {
        method: "PATCH",
      });
      toast.success("Asset Published Successfully");
      setDetailBar(false);
      setBtnLoading(false);
      setAssets((prevAssets) =>
        prevAssets.map((asset) =>
          asset.asset_id === id
            ? { ...asset, asset_status: "published" }
            : asset
        )
      );
    } catch (error) {
      toast.error(getErrorMessage(error));
      setBtnLoading(false);
    }
  };

  const handleDeleteAsset = async () => {
    try {
      const apiUrl = `/assets/delete-asset/${openModal}`;
      const response = await apiCall(apiUrl, {
        method: "DELETE",
      });
      toast.success("Asset Deleted Successfully");
      setAssets(assets.filter((asset) => asset?.asset_id !== openModal));
      setDetailBar(false);
    } catch (error) {
      toast.error(getErrorMessage(error));
    }
  };

  return (
    <div className="mx-auto max-w-3xl h-full space-y-6 pt-4 relative">
      <div className="space-y-2">
        <div className="flex cursor-pointer justify-between text-end px-5">
          <div className="size-16">
            <img
              src={asset.image || ""}
              alt="img"
              height={1000}
              width={1000}
              quality={100}
              className="h-full w-full object-contain opacity-85"
            />
          </div>
          <RxCross2
            size={25}
            onClick={() => {
              setDetailBar(false), setHighlight(false);
            }}
            className="font-bold text-red-600"
          />
        </div>
        <div className="custom-scrollbar h-[calc(100vh-340px)] overflow-auto ">
          <div className="px-5 border-b border-primary pb-3">
            <p className="font-concur font-semibold">{asset.asset_name}</p>

            <div className="mt-1 flex flex-wrap gap-2">
              <Tag
                variant="solidBlue"
                label={asset.category}
                className="text-xs capitalize"
              />
            </div>
          </div>

          <div className="sm:col-span-2 px-5">
            <p className="mt-4 font-lato text-xs text-subHeading">
              {asset.description}
            </p>
          </div>

          <div className="px-5">
            <p className="mt-3 font-concur text-base text-black">Status</p>
            <Tag
              variant={
                asset.asset_status == "published"
                  ? "active"
                  : asset.asset_status == "archived"
                  ? "inactive"
                  : "draft"
              }
              label={asset.asset_status}
              className="w-24 text-xs capitalize"
            />
          </div>

          <div className="mt-3 sm:col-span-2 px-5">
            <p className="font-concur text-base text-black">Type</p>
            <div className="mt-1 flex flex-wrap gap-2">
              {asset?.type?.map((type) => (
                <span key={type}>
                  <Tag label={type} className="text-xs capitalize" />
                </span>
              ))}
            </div>
          </div>

          <div className="mt-3 px-5">
            <p className="font-concur text-base text-black">Created At</p>
            <p className="text-sm text-subHeading">
              {dayjs(asset.created_at).format("MMM D, YYYY, h:mm A")}
            </p>
          </div>
        </div>
      </div>
      <div className="flex w-full items-center justify-between absolute border-t border-primary py-2 bottom-0 px-5 gap-4">
        <div className="flex w-full items-center gap-4">
          <Button
            variant="icon"
            onClick={() => {
              setOpenModal(asset.asset_id);
            }}
            disabled={!canWrite("/apps/asset-sku")}
          >
            <LuTrash className="size-5 text-[#d94e4e]" />
          </Button>

          {asset.asset_status == "published" ? (
            ""
          ) : (
            <Button
              variant="icon"
              onClick={() => {
                setOpenModal(asset.asset_id);
              }}
              disabled={!canWrite("/apps/asset-sku")}
            >
              <BiPencil />
            </Button>
          )}
        </div>

        {asset.asset_status != "published" && (
          <Button
            disabled={btnLoading || !canWrite("/apps/asset-sku")}
            btnLoading={btnLoading}
            onClick={() => handlePublishAsset(asset.asset_id)}
            variant="primary"
            className={` ${asset.status == "archived" ? "hidden" : ""} px-4 `}
          >
            Publish
          </Button>
        )}
      </div>
      {openModal && (
        <DeleteModal
          closeModal={closeModal}
          onConfirm={handleDeleteAsset}
          title={"Do you want to delete this "}
          field={"asset?"}
          dpId={openModal}
          typeTitle="Asset"
        />
      )}
    </div>
  );
};

export default DetailSidebar;
