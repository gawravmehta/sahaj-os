  import React from 'react'

  const Profile = () => {
    return (
      <>
        <div className="p-6 px-64">
          <div className="text-center py-5">
            <h6 className="text-gray-600 text-base">BROWSE</h6>
            <h3>
              <span className="text-pink-500 text-4xl">Matrimonial </span> Profiles by
            </h3>
          </div>

          <div className="flex justify-center items-center gap-14  mt-4 mb-6">
            <div className="text-center">
              <div  className="text-gray-800 hover:text-blue-800">Mother Tongue</div>
            </div>

            <div className="text-center">
              <div  className="text-gray-800 hover:text-blue-800">Caste</div>
            </div>

            <div className="text-center">
              <div  className="text-gray-800 hover:text-blue-800">City</div>
            </div>

            <div className="text-center">
              <div  className="text-gray-800 hover:text-blue-800">State</div>
            </div>

            <div className="text-center">
              <div  className="text-gray-800 hover:text-blue-800">NRI</div>
            </div>

            <div className="text-center">
              <div  className="text-gray-800 hover:text-blue-800">College</div>
            </div>
          </div>

          <div className="mt-4 flex flex-wrap justify-center space-x-2 px-16">
            <div  className="text-gray-800 hover:underline">Bihari</div>
            <span>|</span>
            <div  className="text-gray-800 hover:underline">Bengali</div>
            <span>|</span>
            <div  className="text-gray-800 hover:underline">Hindi MP</div>
            <span>|</span>
            <div  className="text-gray-800 hover:underline">Konkani</div>
            <span>|</span>
            <div  className="text-gray-800 hover:underline">Himachali</div>
            <span>|</span>
            <div  className="text-gray-800 hover:underline">Haryanvi</div>
            <span>|</span>
            <div  className="text-gray-800 hover:underline">Assamese</div>
            <span>|</span>
            <div  className="text-gray-800 hover:underline">Kashmiri</div>
            <span>|</span>
            <div  className="text-gray-800 hover:underline">Hindi MP</div>
            <span>|</span>
            <div  className="text-gray-800 hover:underline">Konkani</div>
            <span>|</span>
            <div  className="text-gray-800 hover:underline">Telugu</div>
            <span>|</span>
            <div  className="text-gray-800 hover:underline">Haryanvi</div>
          </div>
        </div>
        <div className="bg-gray-100 p-8 px-64">
          <div className="text-center mb-6">
            {/* <Image src="" alt="Add image" className="mx-auto" /> */}
          </div>

          <div className="text-base leading-7 pt-4 text-gray-700 opacity-80">
            <p className="mb-4">
              Soul Match.com is one of the leading and most trusted matrimony websites in India. Making happy marriages happen since 1998, Soul Match understands the importance of choosing the right partner for marriage, especially in the Indian cultural setup. It believes in providing the most secure and convenient matchmaking experience to all its members by ensuring 100% screening, exclusive privacy options, photo protection features and verification of phone numbers and more information. While the online matrimonial site connects millions of people directly, Soul Match also maintains a dedicated Customer Care team and offers offline Match Point Centers across the country, for deeper and personal interaction with prospective brides, grooms and/or families.
            </p>
            <small className="block">
              Please note: Soul Match is only meant for users with a bonafide intent to enter into a matrimonial alliance and is not meant for users interested in dating only. Soul Match platform should not be used to post any obscene material, such actions may lead to permanent deletion of the profile used to upload such content.
            </small>
          </div>
        </div>
      </>
    )
  }

  export default Profile
