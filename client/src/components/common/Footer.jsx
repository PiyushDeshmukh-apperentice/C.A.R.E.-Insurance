import React from "react";
import Button from "../ui/Button";
import useReveal from "../../hooks/useReveal";

const Footer = () => {
  const navigationSections = [
    {
      // title: "Pages",
      links: [
        // { label: "Home V.1", href: "/" },
        // { label: "Home V.2", href: "/home-v2" },
        // { label: "Home V.3", href: "/home-v3" },
        { label: "About", href: "/about" },
      ],
    },
    {
      // title: "Pages",
      links: [
        // { label: "Services V.1", href: "/services-v1" },
        // { label: "Services V.2", href: "/services-v2" },
        // { label: "Services V.3", href: "/services-v3" },
        { label: "Internal Services", href: "/internal-services" },
      ],
    },
    {
      // title: "Pages",
      links: [
        // { label: "Get a Quote", href: "/quote" },
        // { label: "Blog", href: "/blog" },
        // { label: "Internal Blogs", href: "/internal-blogs" },
        // { label: "Contact V.1", href: "/contact-v1" },
      ],
    },
    {
      // title: "Pages",
      links: [
        // { label: "Contact V.2", href: "/contact-v2" },
        // { label: "Contact V.3", href: "/contact-v3" },
      ],
    },
  ];

  const [heroRef, heroVisible] = useReveal();

  return (
    <section
      ref={heroRef}
      className={`
        w-full
        transition-all
        duration-700
        ease-out
        ${heroVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"}
      `}
      style={{ backgroundColor: "var(--bg-highlight)" }}
    >
    <footer className="w-full" style={{ backgroundColor: "var(--bg-footer)" }}>
      <div className="max-w-[1440px] mx-auto px-4 sm:px-6 lg:px-20 py-16 lg:py-20">
        <div className="flex flex-col gap-12 lg:gap-16">

          {/* Get in Touch Section */}
          <div className="w-full">
            <div
              className="rounded-[20px] p-8 sm:p-10 lg:p-12"
              style={{ backgroundColor: "var(--primary-background)" }}
            >
              <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-8 lg:gap-12">

                {/* Left Content */}
                <div className="flex-1 space-y-8">
                  <img
                    src="/images/img_component_1_white_a700_30x38.svg"
                    alt="InsureGuard Pro"
                    className="w-10 h-8"
                  />

                  <h2
                    className="font-normal"
                    style={{
                      fontSize: "var(--font-size-5xl)",
                      lineHeight: "var(--line-height-5xl)",
                      color: "var(--primary-foreground)",
                    }}
                  >
                    Get in Touch
                  </h2>

                  <p
                    className="max-w-lg"
                    style={{
                      fontSize: "var(--font-size-base)",
                      lineHeight: "var(--line-height-xl)",
                      color: "var(--primary-foreground)",
                    }}
                  >
                    You can also use the feedback form below to reach out to us
                    directly through our website.
                  </p>

                  <Button
                    text="Contact Us"
                    text_color="text-[#0c204b]"
                    fill_background_color="bg-white"
                    border_border_radius="rounded-[12px]"
                    padding="py-3 px-8"
                    className="hover:opacity-90 transition-opacity duration-200"
                  />
                </div>

                {/* Right Animated Image */}
                <div className="relative w-full lg:w-auto lg:shrink-0">
                  <div className="relative w-full max-w-[514px] h-[280px] lg:h-[308px] mx-auto animate-[float_6s_ease-in-out_infinite]">
                    
                    {/* Main Image */}
                    <img
                      src="/images/img_component_1_white_a700_308x514.png"
                      alt="Insurance illustration"
                      className="w-full h-full object-cover rounded-[20px]"
                    />

                    {/* Floating Icons */}
                    <img
                      src="/images/img_component_1_teal_400_80x92.png"
                      alt="Arrow icon"
                      className="absolute top-6 right-6 w-[92px] h-[80px] animate-[float_4.5s_ease-in-out_infinite]"
                    />

                    <img
                      src="/images/img_component_1_102x82.png"
                      alt="Badge"
                      className="absolute bottom-6 left-6 w-[82px] h-[102px] animate-[float_6.5s_ease-in-out_infinite]"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Footer Links */}
          <div className="flex flex-col lg:flex-row gap-12 lg:gap-16">
            <div className="w-full lg:w-[350px] space-y-8">
              <img
                src="/images/img_component_1_blue_gray_900_30x114.png"
                alt="Sureva Logo"
                className="w-[114px] h-[30px]"
              />

              <p
                className="max-w-md"
                style={{
                  fontSize: "var(--font-size-base)",
                  lineHeight: "var(--line-height-xl)",
                  color: "var(--text-muted)",
                }}
              >
                Innovative legal strategies paired with outstanding service. Our
                legal expertise and talent are tailored to meet the evolving
                needs.
              </p>
            </div>

            {/* <div className="flex-1 grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-12">
              {navigationSections.map((section, sectionIndex) => (
                <div key={sectionIndex} className="space-y-6">
                  <h3
                    style={{
                      fontSize: "var(--font-size-xl)",
                      color: "var(--text-muted)",
                    }}
                  >
                    {section.title}
                  </h3>

                  <ul className="space-y-4">
                    {section.links.map((link, linkIndex) => (
                      <li key={linkIndex}>
                        <a
                          href={link.href}
                          className="hover:opacity-70 transition-opacity"
                          style={{
                            fontSize: "var(--font-size-base)",
                            color: "var(--text-muted)",
                          }}
                        >
                          {link.label}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div> */}
          </div>
        </div>
      </div>

      {/* Animation keyframes */}
      <style>{`
        @keyframes float {
          0%, 100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-12px);
          }
        }
      `}</style>
    </footer>
    </section>
  );
};

export default Footer;
