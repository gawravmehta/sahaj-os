"use client";

import { FaUserCircle } from 'react-icons/fa';
import { BiArrowBack } from "react-icons/bi";
import Link from 'next/link';
import { useRouter } from 'next/navigation';

const UserProfile = () => {
  const router = useRouter();
  return (
    <div className="min-h-screen bg-gray-100 flex justify-center items-center p-4 lg:p-10">
      <div className="bg-white rounded-2xl shadow-lg w-full max-w-6xl lg:flex lg:space-x-12 p-8 lg:p-12">
        {/* Left Section - Profile Picture & Personal Info */}
        <div className="lg:w-1/3 flex flex-col items-center lg:items-start">
          <Link href="/matrimonial/dashboard">
            <div className="text-gray-500 hover:text-gray-700 cursor-pointer mb-6">
              <BiArrowBack size={24} />
            </div>
          </Link>

          {/* Profile Picture */}
          <div className="w-40 h-40 rounded-full bg-gray-200 mb-6 overflow-hidden flex items-center justify-center shadow-lg">
            <FaUserCircle size={150} className="text-gray-300" />
          </div>

          {/* Name & Title */}
          <h1 className="text-3xl lg:text-4xl font-bold text-gray-800 mb-2">
            Ravi Sharma
          </h1>
          <p className="text-lg text-gray-500 mb-4">
            Software Developer at Infosys
          </p>

          {/* Personal Details */}
          <div className="mt-6 w-full">
            <h2 className="text-xl font-semibold text-gray-700 mb-4">
              Personal Details
            </h2>
            <ul className="space-y-2 text-gray-600">
              <li><strong>Date of Birth:</strong> 10th March 1990</li>
              <li><strong>Mother Tongue:</strong> Hindi</li>
              <li><strong>Religion:</strong> Hindu</li>
              <li><strong>Marital Status:</strong> Single</li>
              <li><strong>Height:</strong> 5&apos;9&quot;</li>
              <li><strong>Country:</strong> India</li>
              <li><strong>Degree:</strong> B.Tech in Computer Science</li>
              <li><strong>Employed In:</strong> Private</li>
              <li><strong>Annual Income:</strong> ₹10,00,000</li>
            </ul>
          </div>
        </div>

        {/* Right Section - Family Details & More */}
        <div className="lg:w-2/3 mt-10 lg:mt-0">
          {/* Family Details */}
          <div className="mb-10">
            <h2 className="text-2xl font-semibold text-gray-700 mb-4">
              Family Details
            </h2>
            <ul className="space-y-2 text-gray-600">
              <li><strong>Family Type:</strong> Nuclear</li>
              <li><strong>Father&apos;s Occupation:</strong> Government Employee</li>
              <li><strong>Mother&apos;s Occupation:</strong> Homemaker</li>
              <li><strong>Contact Address:</strong> 123 Street, Delhi, India</li>
            </ul>
          </div>

          {/* About Family */}
          <div className="mb-10">
            <h2 className="text-2xl font-semibold text-gray-700 mb-4">
              About Family
            </h2>
            <p className="text-gray-600 leading-relaxed">
              We are a simple and down-to-earth family. My father works for the
              government, and my mother is a homemaker. We value traditions and
              believe in maintaining a good balance between modern and cultural
              values.
            </p>
          </div>

          {/* Express Yourself */}
          <div className="mb-10">
            <h2 className="text-2xl font-semibold text-gray-700 mb-4">
              Express Yourself
            </h2>
            <p className="text-gray-600 leading-relaxed">
              I am passionate about software development and enjoy working on
              new and challenging projects. I like to keep myself updated with
              the latest technology trends. In my free time, I enjoy traveling,
              reading, and cooking.
            </p>
          </div>

          {/* Edit Button */}
          <div className="flex justify-center lg:justify-start">
            <button onClick={()=>router.push("/matrimonial/personal_details")} className="px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow-lg hover:bg-blue-500 hover:scale-105 transition-all">
              Edit Profile
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;
