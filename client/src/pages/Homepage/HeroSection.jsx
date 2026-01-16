import React from "react";
import Button from "../../components/ui/Button";
import useReveal from "../../hooks/useReveal";

const HeroSection = () => {
  const [heroRef, heroVisible] = useReveal();

  return (
    <section
      ref={heroRef}
      className={`
        w-full
        transition-all
        duration-1000
        ease-out
        ${heroVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-8"}
      `}
      style={{ backgroundColor: "var(--bg-highlight)" }}
    >
      <div className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-20 py-8 sm:py-12 lg:py-16">

        {/* HERO CONTENT */}
        <div className="flex flex-col items-center text-center space-y-4">

          {/* Rating Badge */}
          <div
            className={`
              inline-flex items-center gap-2 rounded-full px-5 py-2 shadow-sm
              transition-all duration-700 ease-out delay-0
              ${heroVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"}
            `}
            style={{ backgroundColor: "var(--secondary-background)" }}
          >
            <div
              className="w-6 h-6 rounded-full flex items-center justify-center"
              style={{ backgroundColor: "#10b981" }}
            >
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path
                  d="M11.6667 3.5L5.25 9.91667L2.33333 7"
                  stroke="white"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </div>
            <span
              className="font-normal"
              style={{
                fontSize: "var(--font-size-base)",
                lineHeight: "var(--line-height-base)",
                color: "var(--text-primary)",
              }}
            >
              4.9 Rated By real users
            </span>
          </div>

          {/* HEADLINE */}
          <h1
            className={`
              font-['Roboto_Serif'] font-normal max-w-4xl
              transition-all duration-800 ease-out delay-150
              ${heroVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"}
            `}
            style={{
              fontSize: "clamp(34px, 5vw, 56px)",
              lineHeight: "1.15",
              color: "var(--text-primary)",
            }}
          >
            Your perfect policy,
            <br />
            fast & affordable
          </h1>

          {/* DESCRIPTION */}
          <p
            className={`
              max-w-xl font-normal
              transition-all duration-800 ease-out delay-300
              ${heroVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"}
            `}
            style={{
              fontSize: "var(--font-size-base)",
              lineHeight: "var(--line-height-lg)",
              color: "var(--text-muted)",
            }}
          >
            Get a free quote in under 2 minutes. Experience peace of mind with our
            reliable insurance options.
          </p>

          {/* CTA */}
          <div
            className={`
              pt-2
              transition-all duration-800 ease-out delay-500
              ${heroVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"}
            `}
          >
            <button
                className="bg-(--primary-background) cursor-pointer font-[Inter] leading-5 text-white rounded-[14px] py-3 px-6
                hover:scale-105
                transition-transform duration-300 ease-out"
              >
                Why Choose Us
              </button>
          </div>
        </div>

        {/* HERO IMAGES */}
        <div className="relative mt-10 lg:mt-14">
          <div className="flex justify-center items-end relative">

            {/* Family Illustration */}
            <div className="relative w-full max-w-[680px] animate-[float_10s_ease-in-out_infinite]">
              <img
                src="/images/img_component_1_black_900_01.png"
                alt="Happy family with insurance protection"
                className="w-full h-auto"
              />

              {/* Top-right Icon */}
              <img
                src="/images/img_component_1_teal_400.png"
                alt="Insurance icon"
                className="absolute -top-6 -right-4 sm:-right-8 w-[80px] sm:w-[110px] animate-[float_8s_ease-in-out_infinite]"
              />
            </div>
          </div>

          {/* FLOATING BADGES */}
          <div className="absolute left-0 sm:left-8 lg:left-16 top-[38%] hidden sm:block animate-[float_9s_ease-in-out_infinite]">
            <Badge text="Insurance Made Easy" />
          </div>

          <div className="absolute left-4 sm:left-12 lg:left-20 bottom-[18%] hidden sm:block animate-[float_12s_ease-in-out_infinite]">
            <img
              src="/images/img_component_1_pink_100.png"
              alt="Ribbon"
              className="absolute -left-10 -top-6 w-[60px] lg:w-[82px]"
            />
            <Badge text="Trusted Coverage" />
          </div>

          <div className="absolute right-0 sm:right-8 lg:right-16 top-1/2 hidden sm:block animate-[float_11s_ease-in-out_infinite]">
            <Badge text="Smart Insurance" />
          </div>
        </div>
      </div>

      {/* ANIMATIONS */}
      <style>{`
        @keyframes float {
          0%, 100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-10px);
          }
        }

        @keyframes pulse-soft {
          0%, 100% {
            transform: scale(1);
          }
          50% {
            transform: scale(1.02);
          }
        }
      `}</style>
    </section>
  );
};

const Badge = ({ text }) => (
  <div
    className="
      flex items-center gap-2 px-4 py-2 rounded-full shadow-lg
      transition-all duration-500 ease-out
      hover:-translate-y-1 hover:shadow-xl
    "
    style={{ backgroundColor: "var(--secondary-background)" }}
  >
    <div
      className="w-5 h-5 rounded-full flex items-center justify-center"
      style={{ backgroundColor: "#10b981" }}
    >
      <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
        <path
          d="M10 3L4.5 8.5L2 6"
          stroke="white"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </div>
    <span
      className="font-normal text-sm whitespace-nowrap"
      style={{ color: "var(--text-primary)" }}
    >
      {text}
    </span>
  </div>
);

export default HeroSection;
