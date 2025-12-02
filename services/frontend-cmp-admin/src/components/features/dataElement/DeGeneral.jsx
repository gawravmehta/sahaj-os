import DateTimeFormatter from "@/components/ui/DateTimeFormatter";
import NoDataFound from "@/components/ui/NoDataFound";

const DeGeneral = ({ deData }) => {
  return (
    <div className="mt-5 h-full w-full pb-6">
      <div className="flex w-full items-center justify-center">
        {deData ? (
          <div className="mx-auto w-full max-w-3xl rounded-sm px-4 sm:px-6">
            <div className="flex w-full flex-col gap-4">
              <div className="flex justify-between">
                <div>
                  <h1 className="mb-1 font-lato text-sm text-subHeading">
                    Name:
                  </h1>
                  <p className="font-lato capitalize">
                    {deData.de_name || "N/A"}
                  </p>
                </div>
                <button
                  className={`h-8 cursor-default rounded-full px-4 text-sm capitalize ${
                    deData.de_status === "draft"
                      ? "bg-gray-200 text-gray-500"
                      : deData.de_status === "published"
                      ? "bg-[#e1ffe7] text-[#06a42a]"
                      : deData.de_status === "archived"
                      ? "bg-[#fbeaea] text-[#d94e4e]"
                      : "bg-gray-100 text-white"
                  }`}
                >
                  {deData.de_status}
                </button>
              </div>
              <div className="flex w-full justify-between">
                <div>
                  <h1 className="mb-1 font-lato text-sm text-subHeading">
                    Original Name:
                  </h1>
                  <p>{deData.de_original_name || "N/A"}</p>
                </div>
              </div>
              <div className="">
                <h1 className="mb-1 font-lato text-sm text-subHeading">
                  Description:
                </h1>
                <p className="font-lato">{deData.de_description || "N/A"}</p>
              </div>
              <div>
                <h1 className="mb-1 font-lato text-sm text-subHeading">
                  Data Element Hash ID:
                </h1>
                <p className="font-lato">{deData.de_hash_id || "N/A"}</p>
              </div>
              <div className="grid grid-cols-2 gap-10">
                <div className="">
                  <h1 className="mb-1 font-lato text-sm text-subHeading">
                    Core Identifier:
                  </h1>
                  <p className="font-lato">
                    {deData.is_core_identifier ? "Yes" : "No"}
                  </p>
                </div>

                <div className="">
                  <h1 className="mb-1 font-lato text-sm text-subHeading">
                    Sensitivity:
                  </h1>
                  <p className="capitalize">{deData.de_sensitivity}</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-10">
                <div className="">
                  <h1 className="mb-1 font-lato text-sm text-subHeading">
                    Data Type:
                  </h1>
                  <p className="font-lato">{deData.de_data_type || "N/A"}</p>
                </div>
                <div className="">
                  <h1 className="mb-1 font-lato text-sm text-subHeading">
                    Retention Period:
                  </h1>
                  <p className="font-lato">
                    {deData.de_retention_period || "N/A"}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-10">
                <div className="">
                  <h1 className="mb-1 font-lato text-sm text-subHeading">
                    Created At:
                  </h1>
                  <p className="">
                    <DateTimeFormatter
                      className="flex gap-1 text-sm"
                      dateTime={deData.created_at}
                    />
                  </p>
                </div>
                <div className="">
                  <h1 className="mb-1 font-lato text-sm text-subHeading">
                    Last Updated:
                  </h1>
                  <p>
                    <DateTimeFormatter
                      className="flex gap-1 text-sm"
                      dateTime={deData.last_updated}
                    />
                  </p>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <NoDataFound />
        )}
      </div>
    </div>
  );
};

export default DeGeneral;
