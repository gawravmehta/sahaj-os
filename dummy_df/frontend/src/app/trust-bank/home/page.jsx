"use client";

import Footer from "@/components/bankComps/Footer";
import Navbar from "@/components/bankComps/Navbar";

export default function HomePage() {
  return (
    <div>
      <div className="fixed top-0 w-full">
        <Navbar />
      </div>

      {/* Hero Section */}
      <section className="bg-gray-800 text-white py-20 mt-16">
        <div className="container mx-auto px-6 text-center">
          <h1 className="text-4xl font-bold mb-2">Welcome to Our Service</h1>
          <p className="text-lg mb-8">
            Experience the best credit card offers and benefits tailored for
            you.
          </p>
          <a
            href="#"
            className="bg-primary text-white  px-6 py-3 rounded-lg shadow hover:bg-gray-600"
          >
            Get Started
          </a>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-6">
          <h2 className="text-3xl font-semibold text-center mb-12">
            Why Choose Us?
          </h2>
          <div className="flex flex-wrap justify-center">
            <div className="w-full md:w-1/3 px-6 mb-12">
              <div className="bg-gray-100 h-[250px] p-6 rounded-lg shadow-lg text-center">
                <a href="/trust-bank/loan-auth" className="">
                  <div className="mb-4 text-primary">
                    <i className="fas fa-credit-card fa-2x"></i>
                  </div>
                  <h3 className="text-xl font-semibold mb-4">Home Loans</h3>
                  <p className="text-gray-600">
                    Make your homeownership dream a reality with our competitive
                    home loan options. Whether buying, refinancing, or
                    investing, we provide flexible terms and personalized
                    support to ensure a smooth, stress-free mortgage process.
                  </p>
                </a>
              </div>
            </div>
            <div className="w-full md:w-1/3 px-6 mb-12">
              <div className="bg-gray-100 h-[250px] p-6 rounded-lg shadow-lg text-center">
                <a href="/trust-bank/credit" className="">
                  <div className="mb-4 text-primary">
                    <i className="fas fa-shield-alt fa-2x"></i>
                  </div>
                  <h3 className="text-xl font-semibold mb-4">Credit Cards</h3>
                  <p className="text-gray-600">
                    Discover our range of credit cards offering low interest
                    rates, cashback rewards, and exclusive perks like travel
                    benefits and shopping discounts. Enjoy financial flexibility
                    with secure, easy-to-use credit solutions designed to fit
                    your lifestyle and spending habits.
                  </p>
                </a>
              </div>
            </div>
            <div className="w-full md:w-1/3 px-6 mb-12">
              <div className="bg-gray-100 h-[250px] p-6 rounded-lg shadow-lg text-center">
                <a href="/trust-bank/insurance" className="">
                  <div className="mb-4 text-primary">
                    <i className="fas fa-user-tie fa-2x"></i>
                  </div>
                  <h3 className="text-xl font-semibold mb-4">Insurance</h3>
                  <p className="text-gray-600">
                    Safeguard your future with our comprehensive insurance
                    plans, including health, life, auto, and home coverage. Our
                    24/7 dedicated support team ensures you have the protection
                    you need, offering expert guidance and peace of mind.
                  </p>
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Call to Action Section */}
      <section className="bg-primary  py-20">
        <div className="container mx-auto px-6 text-center">
          <h2 className="text-3xl font-semibold mb-6">
            Ready to Get Your Credit Card?
          </h2>
          <p className="text-lg mb-8">
            Join thousands of satisfied customers and enjoy exclusive benefits.
          </p>
          <a
            href="/trust-bank/credit"
            className="bg-white text-primary px-6 py-3 rounded-lg shadow hover:bg-gray-200"
          >
            Apply Now
          </a>
        </div>
      </section>

      <Footer />
    </div>
  );
}
