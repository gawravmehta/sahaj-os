import NoDataFound from "@/components/ui/NoDataFound";
import Tag from "@/components/ui/Tag";
import TranslationsList from "../../shared/TranslationsList";

const DeGovernance = ({ deData }) => {
  return (
    <div className=" w-full">
      <div className="flex">
        {deData ? (
          <div className="mx-auto w-full max-w-3xl rounded-sm px-4 sm:px-6 h-[calc(100vh-175px)] overflow-y-auto custom-scrollbar ">
            <div className="flex w-full flex-col gap-4">
              <div className="">
                <h1 className="mb-1 mt-5 font-lato text-sm text-subHeading">
                  Data Element Translations:
                </h1>
                <TranslationsList formState={deData} />
              </div>
              <div className="">
                <h1 className="mb-1 font-lato text-sm text-subHeading">
                  Collection Points:
                </h1>
                <div className="space-y-2">
                  {deData.collection_points?.length > 0 ? (
                    deData.collection_points.map((point) => (
                      <Tag
                        key={point.cp_id}
                        className="cursor-default"
                        variant="secondary"
                      >
                        {point.cp_name || "Unnamed Collection Point"}
                      </Tag>
                    ))
                  ) : (
                    <p className="text-gray-500">No Collection Points</p>
                  )}
                </div>
              </div>
              <div className="">
                <h1 className="mb-1 font-lato text-sm text-subHeading">
                  Purposes:
                </h1>
                <div className="space-y-2 ">
                  {deData.purposes?.length > 0 ? (
                    deData.purposes.map((point, index) => (
                      <p key={point.purpose_id} className="">
                        {index + 1} {point.purpose_name || "Unnamed Purpose"}
                      </p>
                    ))
                  ) : (
                    <p className="text-gray-500">No Purposes Attached</p>
                  )}
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

export default DeGovernance;
