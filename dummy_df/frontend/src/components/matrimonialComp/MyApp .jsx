import Image from 'next/image'
// import pic from '../public/images/Group_64_new.png'
// import img from '../public/images/logo_apple.png'

const MyApp = () => {
    return (
        <article className='px-64'>
            <div className="flex justify-between h-[390px] bg-[#34495e]  text-white">
                <div className="w-[36%] pl-14 pt-7 pb-14 flex flex-col">
                    <h3>
                        <div className="text-sm pb-1.5 font-bold  tracking-widest text-white">
                            STAY CONNECTED WITH
                        </div>
                        <div className="text-2xl pb-2 font-medium text-white">
                            Soul Match Apps
                        </div>
                    </h3>
                    <div className="pb-5 text-sm leading-7  text-white">
                        Access quick &amp; simple search, instant updates and a great user experience on your phone. Download our apps rated best in the online matrimony segment.
                    </div>
                    <div className="flex justify-between w-[90%] pb-5">
                        <div>
                            <a target="_blank" rel="noopener noreferrer" href="#">
                                <div className="appsSprite apps1">
                                    <Image src="/logoApple.png" alt='Apple Logo' width={400} height={400} />
                                </div>
                            </a>
                        </div>
                        <div>
                            <a target="_blank" rel="noopener noreferrer" href="#">
                                <div className="appsSprite apps2">
                                    <Image  src="/logoApple.png" alt='Apple Logo' width={400} height={400}/>
                                </div>
                            </a>
                        </div>
                    </div>
                    <div className="text-lg text-white">
                        <a href="#" className='text-blue-600 hover:underline'>
                            <span className="font-medium text-gray-100">Click here</span>
                        </a>
                        <span className="text-gray-400"> to view more about Apps</span>
                    </div>
                </div>
                <div className="w-[46%] pt-5 relative">
                    <Image  
                        id="grp64"
                        className="absolute bottom-0 h-80 w-96"
                        src="/PhoneImage.png" 
                        alt="Group Image" 
                        // layout="fill"
                        objectFit="cover"
                        height={300}
                        width={300}
                    />
                </div>
            </div>
        </article>
    )
}

export default MyApp;
