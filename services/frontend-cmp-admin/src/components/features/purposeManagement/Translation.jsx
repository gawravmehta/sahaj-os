"use client";
import TranslationsList from "@/components/shared/TranslationsList";
import Image from "next/image";


const Translation = ({ dpData }) => {


  return (
    <>
      <div className="flex items-center justify-center">
        <div className="  ">
        {dpData?.translations ? (
           <div className="w-225 m-auto  ">
           <TranslationsList formState={dpData} useScroll={true} height={"190px"}/>
          </div>
          ) : (
            <div className="flex min-h-[calc(100vh-250px)] items-center justify-center">
              <div className="flex flex-col items-center justify-center">
                <div className="w-52">
                  <Image
                    height={200}
                    width={200}
                    src="/assets/illustrations/no-data-find.png"
                    alt="Circle Image"
                    className="h-full w-full object-cover"
                  />
                </div>
                <div>
                  <p className="mt-2 text-subText">
                    {" "}
                    No translations available
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default Translation;
