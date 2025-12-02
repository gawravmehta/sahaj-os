import { MdCheckCircle, MdCancel } from 'react-icons/md';

const MembershipPlans = () => {
    return (
        <article className="text-center -mt-5 px-64 ">
            <div className="bg-gray-50  shadow-md  relative ">
               
                    <div className="text-2xl my-3 font-bold text-black  pt-16">
                        <span className="text-pink-500">Membership </span>Plans
                    </div>
                
                <div className="text-gray-600 text-sm mb-10 leading-6 px-20 ">
                    Upgrade your plan as per your customized requirements. With a paid membership, you can seamlessly connect with your prospects and get more responses. Here are some key benefits:
                </div>

                <div className="flex items-center justify-center">
                    <div className="w-80 text-left p-4 z-30 bg-white shadow-md rounded-sm ">
                        <div className="bg-pink-500 h-1 rounded-full w-16 mb-2"></div>
                        <div className="text-2xl font-semibold mb-2">Free</div>
                        <div className="flex items-center mb-5 text-sm"><MdCheckCircle className="text-pink-500 mr-2 " />Browse Profiles</div>
                        <div className="flex items-center mb-5 text-sm"><MdCheckCircle className="text-pink-500 mr-2" />Shortlist & Send Interest</div>
                        <div className="flex items-center mb-5 text-sm"><MdCheckCircle className="text-pink-500 mr-2" />Message and chat with unlimited users</div>
                        <span className="text-gray-400">
                            <div className="flex items-center mb-5 text-sm"><MdCancel className="text-gray-400 mr-2" />Get up to 3x more matches daily</div>
                            <div className="flex items-center mb-5 text-sm"><MdCancel className="text-gray-400 mr-2" />Unlock access to advanced search</div>
                            <div className="flex items-center mb-5 text-sm"><MdCancel className="text-gray-400 mr-2" />View contact details</div>
                            <div className="flex items-center mb-5"><MdCancel className="text-gray-400 mr-2" />Make unlimited voice and video calls</div>
                        </span>
                        <a href="#" className="block text-center mt-4 py-2 px-4 bg-pink-500 text-white rounded-sm font-bold">
                            Register Free
                        </a>
                    </div>

                    <div className="bg-pink-500 text-white text-left px-4 py-7 z-30 rounded-sm shadow-md w-80">
                        <div className="bg-white h-1 rounded-full w-16 mb-2"></div>
                        <div className="text-2xl font-semibold mb-2">Paid</div>
                        <div className="flex items-center mb-8 text-sm"><MdCheckCircle className="text-white mr-2" />Shortlist & Send Interest</div>
                        <div className="flex items-center mb-8 text-sm"><MdCheckCircle className="text-white mr-2" />Message and chat with unlimited users</div>
                        <div className="flex items-center mb-8 text-sm"><MdCheckCircle className="text-white mr-2" />Get up to 3x more matches daily</div>
                        <div className="flex items-center mb-8 text-sm"><MdCheckCircle className="text-white mr-2" />Browse Profiles</div>
                        <div className="flex items-center mb-8 text-sm"><MdCheckCircle className="text-white mr-2" />Unlock access to advanced search</div>
                        <div className="flex items-center mb-8 text-sm"><MdCheckCircle className="text-white mr-2" />View contact details</div>
                        <div className="flex items-center mb-8 text-sm"><MdCheckCircle className="text-white mr-2" />Make unlimited voice and video calls</div>
                        <a href="#" className="block text-center mt-4 py-2 px-4 bg-white text-pink-500 rounded-sm font-bold">
                            Browse Membership Plans
                        </a>
                    </div>
                </div>
                <div className='h-60 w-full bg-slate-700  absolute top-[70%]'>

                </div>
            </div>
        </article>
    );
};

export default MembershipPlans;
