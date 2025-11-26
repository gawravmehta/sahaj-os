import Tag from "@/components/ui/Tag";
import Image from "next/image";
import React from "react";

const Legal = ({ dpData }) => {
  if (!dpData) {
    return (
      <div className="p-6">
        <div className="flex min-h-[calc(100vh-270px)] items-center justify-center">
          <div className="flex flex-col items-center justify-center">
            <div className="w-[200px]">
              <Image
                height={200}
                width={200}
                src="/assets/illustrations/no-data-find.png"
                alt="Circle Image"
                className="h-full w-full object-cover"
              />
            </div>
            <div className="mt-5">
              <p>No Legal Available</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center">
      <div className="mt-6 flex h-[calc(100vh-240px)] max-w-3xl justify-center">
        <div className="flex w-225 justify-between px-3">
          <div className="flex flex-col gap-4">
            {dpData?.data_elements?.length > 0 && (
              <div>
                <h1 className="text-[#737c7c]">Data Elements:</h1>
                <div className="mt-2 flex flex-col gap-4">
                  {dpData.data_elements.map((item) => (
                    <div key={item.de_id} className="border-b pb-2">
                      <div className=" flex flex-wrap">
                      <Tag variant="outlineBlue" label={item.de_name} />
                      
                      </div>

                      {item.service_mandatory && (
                        <div className="mt-2">
                          <h2 className="text-[#737c7c]">Service Mandatory:</h2>
                          <p className="text-[16px]">{item.service_message}</p>
                        </div>
                      )}

                      {item.legal_mandatory && (
                        <div className="mt-2">
                          <h2 className="text-[#737c7c]">Legal Mandatory:</h2>
                          <p className="text-[16px]">{item.legal_message}</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {dpData.collection_points?.length > 0 && (
              <div>
                <h1 className="text-[#737c7c]">Collection Points:</h1>
                <div className="mt-2 flex flex-wrap gap-2 text-sm">
                  {dpData.collection_points.map((item) => (
                    <Tag
                      key={item.collection_point_id}
                      variant="lightBlue"
                      label={item.collection_point_name}
                    />
                  ))}
                </div>
              </div>
            )}
            <div className="">
              {dpData?.service_mandatory_de?.length > 0 && (
                <div>
                  <h1 className="text-[#737c7c]">Service Mandatory</h1>
                  {dpData?.service_mandatory_de?.map((item) => (
                    <p className="mt-2 text-[16px]" key={item?.de_id}>
                      {item?.de_name}
                    </p>
                  ))}
                </div>
              )}
              {dpData?.revocation_message && (
                <div>
                  <h1 className="mt-3 text-[#737c7c]">
                    Service Mandatory Message:
                  </h1>
                  <p className="mt-2 text-[16px]">
                    {dpData?.revocation_message}
                  </p>
                </div>
              )}
            </div>
            {dpData?.legal_revocation_message && (
              <div>
                <h1 className="text-[#737c7c]">Legal Revocation Message:</h1>
                <p className="mt-2 text-[16px]">
                  {dpData.legal_revocation_message}
                </p>
              </div>
            )}
          </div>
          <div className="flex justify-end gap-4">
            <div>
             
              <Tag
                variant="active"
                label={`${dpData.consent_time_period} Day`}
                className="text-md"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Legal;
