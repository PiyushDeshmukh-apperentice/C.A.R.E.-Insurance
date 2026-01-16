import React, { useState } from "react";
import Button from "../ui/Button";
import LoginModal from "../LoginModal";

const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const navigationItems = [
    { label: "Home", href: "/", active: true },
    { label: "About Us", href: "/home-v2" },
    { label: "Contact", href: "/home-v3" },
  ];
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);

  // const pagesDropdownItems = ["About", "Services", "Contact", "Blog"];

  return (
    <header className="py-6" style={{ background: 'var(--bg-highlight)' }}>
      <div className="max-w-[1320px] mx-auto px-4">
        {/* Navbar Container */}
        <div className="bg-white rounded-[20px] shadow-sm px-6 lg:px-10">
          <div className="flex justify-between items-center h-[72px]">

            {/* Logo */}
            <div className="flex items-center gap-3">
              <img
                src="/images/img_68b9b823a50348f.png"
                alt="Sureva Logo"
                className="w-[96px] h-auto"
              />
            </div>

            {/* Desktop Navigation */}
            <nav className="hidden lg:flex items-center gap-10">
              <div className="flex items-center gap-6">
                {navigationItems.map((item, index) => (
                  <a
                    key={index}
                    href={item.href}
                    className="transition-colors duration-200"
                    style={{
                      fontSize: "var(--font-size-base)",
                      lineHeight: "var(--line-height-base)",
                      color: item.active
                        ? "var(--text-primary)"
                        : "var(--text-muted)",
                      fontWeight: item.active
                        ? "var(--font-weight-semibold)"
                        : "var(--font-weight-normal)",
                    }}
                  >
                    {item.label}
                  </a>
                ))}
              </div>

              {/* CTA Button */}
              {/* <button
                text="Login"
                text_font_size="text-lg"
                text_font_family="Inter"
                text_font_weight="font-semibold"
                text_line_height="leading-[20px]"
                text_color="text-white"
                fill_background_color="bg-[var(--primary-background)]"
                border_border_radius="rounded-[14px]"
                padding="py-3 px-6"
                className="hover:bg-blue-300 transition-opacity duration-600"
                onClick={() => setIsLoginModalOpen(true)}
              /> */}
              <button
                className="bg-(--primary-background) cursor-pointer text-lg font-[Inter] font-semibold leading-5 text-white rounded-[14px] py-3 px-6
                hover:scale-105
                transition-transform duration-300 ease-out"
                onClick={() => setIsLoginModalOpen(true)}
              >
                Login
              </button>



            </nav>

            {/* Mobile Menu Button */}
            <button
              className="lg:hidden p-2 rounded-lg"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              aria-label="Toggle menu"
              style={{ color: "var(--primary-background)" }}
            >
              <svg
                className="w-6 h-6"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                {isMenuOpen ? (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                ) : (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                )}
              </svg>
            </button>
          </div>

          {/* Mobile Menu */}
          {isMenuOpen && (
            <div className="lg:hidden pb-6">
              <div className="flex flex-col gap-2">
                {navigationItems.map((item, index) => (
                  <a
                    key={index}
                    href={item.href}
                    className="px-4 py-3 rounded-lg transition-colors duration-200 hover:bg-gray-50"
                    style={{
                      fontSize: "var(--font-size-base)",
                      color: item.active
                        ? "var(--text-primary)"
                        : "var(--text-muted)",
                      fontWeight: item.active
                        ? "var(--font-weight-semibold)"
                        : "var(--font-weight-normal)",
                    }}
                    onClick={() => setIsMenuOpen(false)}
                  >
                    {item.label}
                  </a>
                ))}

                <div className="pt-4">
                  <Button
                    text="Get your free quote"
                    text_color="text-white"
                    fill_background_color="bg-[var(--primary-background)]"
                    border_border_radius="rounded-[14px]"
                    className="w-full py-3"
                    onClick={() => setIsMenuOpen(false)}
                  />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
      <LoginModal
        isOpen={isLoginModalOpen}
        onClose={() => setIsLoginModalOpen(false)}
      />
    </header>
  );
};

export default Header;
