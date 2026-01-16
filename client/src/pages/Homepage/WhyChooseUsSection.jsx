import React from "react";
import Button from "../../components/ui/Button";
import useReveal from "../../hooks/useReveal";

const cards = [
  {
    title: "Secure Life coverage",
    desc:
      "Life insurance that safeguards your family's future—simple, affordable, and reliable",
    img: "/images/img_component_1_black_900_01_286x512.png",
    link: "/life-insurance",
  },
  {
    title: "Vital Health assurance",
    desc:
      "Health plans designed for your wellness and wallet, with transparent pricing",
    img: "/images/img_component_1_286x512.png",
    link: "/health-insurance",
  },
  {
    title: "Total Home security",
    desc:
      "Complete home protection against the unexpected, from leaks to natural disasters",
    img: "/images/img_image_2.png",
    link: "/home-insurance",
  },
  {
    title: "Travel insurance",
    desc:
      "Travel smart. Stay protected. Coverage for cancellations, medical emergencies, and delays",
    img: "/images/img_image_1.png",
    link: "/vehicle-insurance",
  },
];

const WhyChooseUsSection = () => {
  const [ref, visible] = useReveal();

  return (
    <section
      ref={ref}
      className={`
        w-full
        transition-all
        duration-1000
        ease-out
        ${visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"}
      `}
      style={{ backgroundColor: "var(--primary-background)" }}
    >
      <div className="max-w-[1200px] mx-auto px-4 sm:px-6 lg:px-20 py-14 lg:py-20">
        <div className="flex flex-col items-center gap-10">

          {/* HEADER */}
          <div
            className={`
              text-center max-w-4xl space-y-4
              transition-all duration-800 ease-out delay-0
              ${visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"}
            `}
          >
            <h2
              className="font-['Roboto_Serif'] font-normal"
              style={{
                fontSize: "var(--font-size-5xl)",
                lineHeight: "1.1",
                color: "var(--primary-foreground)",
              }}
            >
              Why Choose Us?
            </h2>

            <p
              className="font-['Inter'] font-normal max-w-3xl mx-auto"
              style={{
                fontSize: "var(--font-size-base)",
                lineHeight: "var(--line-height-xl)",
                color: "var(--primary-foreground)",
              }}
            >
              We make it easy to protect what matters most. From health and life
              insurance to vehicle and property coverage, we offer smart,
              flexible plans designed to fit your needs and budget.
            </p>
          </div>

          {/* CTA BUTTON */}
          <div
            className={`
              transition-all duration-800 ease-out delay-200
              ${visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"}
            `}
          >
            <Button
              text="Learn more"
              text_font_size="text-base"
              text_font_family="Inter"
              text_font_weight="font-normal"
              text_line_height="leading-[20px]"
              text_color="text-[#0a0a0a]"
              fill_background_color="bg-[#ecece7]"
              border_border_radius="rounded-[12px]"
              padding="py-3 px-8"
              className="hover:opacity-90 transition-opacity duration-200"
            />
          </div>

          {/* CARDS GRID */}
          <div
            className={`
              w-full max-w-4xl
              transition-all duration-800 ease-out delay-300
              ${visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-6"}
            `}
          >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {cards.map((card, index) => (
                <div
                  key={index}
                  className={`
                    bg-white
                    rounded-[16px]
                    p-4
                    flex flex-col
                    justify-between
                    transition-all
                    duration-700
                    ease-out
                    hover:shadow-xl
                    ${
                      visible
                        ? "opacity-100 translate-y-0"
                        : "opacity-0 translate-y-6"
                    }
                  `}
                  style={{ transitionDelay: `${400 + index * 150}ms` }}
                >
                  {/* IMAGE */}
                  <div className="w-full h-[150px] rounded-[12px] bg-gray-50 flex items-center justify-center overflow-hidden group">
                    <img
                      src={card.img}
                      alt={card.title}
                      className="
                        max-h-full
                        max-w-full
                        object-contain
                        scale-105
                        transition-all
                        duration-300
                        ease-out
                        group-hover:scale-110
                        group-hover:-translate-y-1
                      "
                    />
                  </div>

                  {/* CONTENT */}
                  <div className="pt-4 flex flex-col gap-3 text-center flex-1 transition-all duration-500">
                    <h3
                      className="font-['Roboto_Serif'] font-normal"
                      style={{
                        fontSize: "var(--font-size-lg)",
                        lineHeight: "1.3",
                        color: "var(--text-primary)",
                      }}
                    >
                      {card.title}
                    </h3>

                    <p
                      className="font-['Inter'] font-normal text-sm"
                      style={{
                        lineHeight: "var(--line-height-base)",
                        color: "var(--text-muted)",
                      }}
                    >
                      {card.desc}
                    </p>
                  </div>

                  {/* LINK */}
                  <div className="pt-4 text-center transition-all duration-500">
                    <a
                      href={card.link}
                      className="font-['Inter'] font-normal uppercase tracking-widest text-xs hover:opacity-70 transition-opacity"
                      style={{ color: "var(--text-primary)" }}
                    >
                      Learn more
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>
      </div>
    </section>
  );
};

export default WhyChooseUsSection;
