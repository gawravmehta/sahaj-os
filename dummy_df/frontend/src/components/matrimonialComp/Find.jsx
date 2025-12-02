import React from 'react';
import { HiOutlineUserGroup } from 'react-icons/hi';

const Find = () => {
    return (
        <div className=" px-64">
            <div className="  px-16 bg-gray-100 py-10">
                <div className="">
                    <span className="text-base font-semibold text-gray-700">THREE SIMPLE STEPS TO</span>
                </div>
                <h2 className="text-2xl font-bold text-gray-900  mb-10">
                    Find the <span className="text-pink-500">One for You</span>
                </h2>

                <div className="flex justify-around items-start mb-10">
                    <div className="  w-full">
                        <div className="mb-1">
                            <HiOutlineUserGroup className="text-5xl text-pink-500 " />
                        </div>
                        <small className="text-sm text-gray-600">
                            <span className="text-lg font-bold text-gray-800">01.</span> Define Your Partner Preferences
                        </small>
                    </div>

                    <div className="w-full">
                        <div className="mb-1">
                            <HiOutlineUserGroup className="text-5xl text-pink-500 " />
                        </div>
                        <small className="text-sm text-gray-600">
                            <span className="text-lg font-bold text-gray-800">02.</span> Browse Profiles
                        </small>
                    </div>

                    <div className="w-full">
                        <div className="mb-1">
                            <HiOutlineUserGroup className="text-5xl text-pink-500 " />
                        </div>
                        <small className="text-sm text-gray-600">
                            <span className="text-lg font-bold text-gray-800">03.</span> Send Interests & Connect
                        </small>
                    </div>
                </div>

                <div className="text-center">
                    <button className="bg-pink-500 text-white px-11 py-2 rounded-md hover:bg-pink-700 transition">
                        Get Started
                    </button>
                </div>
            </div>
        </div>
    );
}

export default Find;
