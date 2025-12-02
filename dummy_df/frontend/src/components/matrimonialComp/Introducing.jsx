"use client"
import React from 'react';
import { HiOutlineUserGroup } from 'react-icons/hi';
import { FaUserGroup } from "react-icons/fa6";
import { SlUserFollowing } from "react-icons/sl";
import Image from 'next/image';
// import Image from 'next/image';


const Introducing = () => {
    return (

        
        <div className=" p-8 px-64">
            <div className="text-center mb-8 relative h-[70vh]  ">
                <h6 className="text-sm text-gray-700 mt-16">PERSONALISED MATCH-MAKING SERVICE</h6>
                <h3 className="text-2xl my-2 font-bold">
                    Introducing <span className="text-pink-500">Exclusive</span>
                </h3>
                <button className="bg-pink-500 text-white px-4 py-2 mt-4 rounded">EXCLUSIVE</button>
                <div className='absolute w-full top-10'>
                    <Image src="https://allat.one/wp-content/uploads/2022/12/JS_Exclusive_Image_final_min.png" alt="img" height={2000} width={3000} className=' h-[67vh]' />
                </div>

            </div>


            <div className="grid gap-6 md:grid-cols-1 lg:grid-cols-3">
                <div className="bg-white p-6 rounded-lg shadow-md">
                    <div className="flex items-center mb-2">
                        <FaUserGroup className="text-pink-500 text-xl" />
                        <span className="ml-2 text-lg">Meet Your Relationship Manager</span>
                    </div>
                    <p className="text-gray-600">Connect with our highly experienced advisor who manages your profile.</p>
                </div>

                <div className="bg-white p-6 rounded-lg shadow-md">
                    <div className="flex items-center mb-2">
                        <HiOutlineUserGroup className="text-pink-500 text-xl" />
                        <span className="ml-2 text-lg">Communicate your preferences</span>
                    </div>
                    <p className="text-gray-600">Connect with our highly experienced advisor who manages your profile.</p>
                </div>

                <div className="bg-white p-6 rounded-lg shadow-md">
                    <div className="flex items-center mb-2">
                        <SlUserFollowing className="text-pink-500 text-xl" />
                        <span className="ml-2 text-lg font-semibold">Choose from handpicked profiles</span>
                    </div>
                    <p className="text-gray-600">Connect with our highly experienced advisor who manages your profile.</p>
                </div>
            </div>
        </div>
    );
};

export default Introducing;
