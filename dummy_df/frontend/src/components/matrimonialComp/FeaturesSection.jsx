




// components/FeatureSection.js
// import Image from 'next/image';
// import phoneImage from '../public/image.png'; // Adjust the path as necessary

import Image from "next/image";

const FeatureSection = () => {
  return (
    <section
      className="  px-64"
    
    >
      <div className="container mx-auto flex flex-col lg:flex-row items-center bg-gray-50 py-16">
        {/* Text Section */}
        <div className="lg:w-1/2 w-full px-6">
          <p className="text-sm text-gray-500 font-semibold">MEET FROM HOME</p>
          <h2 className="text-4xl font-bold text-black mt-2">
            Impress them{" "}
            <span className="text-pink-500">Over the Distance</span>
          </h2>
          <div className="mt-8 space-y-8">
            <div>
              <h3 className="text-xl font-semibold text-black">
                Soul Match Match Hour
              </h3>
              <div className="w-8 border-b-2 border-pink-500 mt-2 mb-2"></div>
              <p className="text-gray-700">
                Register to join an online event to connect with members of your
                community in a short time
              </p>
            </div>
            <div>
              <h3 className="text-xl font-semibold text-black">
                Voice & Video Calling
              </h3>
              <div className="w-8 border-b-2 border-pink-500 mt-2 mb-2"></div>
              <p className="text-gray-700">
                Enjoy secure conversations using our voice & video calling
                services without revealing your number
              </p>
            </div>
            <div>
              <h3 className="text-xl font-semibold text-black">
                Introducing Video Profiles
              </h3>
              <div className="w-8 border-b-2 border-pink-500 mt-2 mb-2"></div>
              <p className="text-gray-700">
                Stand out amongst others and engage faster! Introduce yourself
                by adding a video to your profile
              </p>
            </div>
          </div>
        </div>

        {/* Image Section */}
        <div className="lg:w-1/2 w-full mt-10 lg:mt-0 px-6 flex justify-center">
          <div className="relative">
            <Image
              src="/PhoneImage.png"
              alt="Phone showing an online event"
              height={200}
              width={300}
            />
            {/* Add any additional badges or icons here */}
          </div>
        </div>
      </div>
    </section>
  );
};

export default FeatureSection;
