import React from 'react';
import Button from '../../components/ui/Button';

const BenefitsSection = () => {
  const benefits = [
    {
      icon: "/images/img_component_1_blue_gray_900.svg",
      title: "Speed You Can Rely On",
      description: "From instant quotes to 48-hour claims processing, we save you time (and stress)."
    },
    {
      icon: "/images/img_component_1_blue_gray_900.svg", 
      title: "Personalized Coverage",
      description: "No two policies are alike—we tailor plans to fit your budget and needs, not the other way around."
    },
    {
      icon: "/images/img_component_1_blue_gray_900.svg",
      title: "Always in Your Corner", 
      description: "24/7 U.S.-based support, whether you are filing a claim at 3 AM or just have a question."
    },
    {
      icon: "/images/img_component_1_blue_gray_900.svg",
      title: "24/7 Customer Support",
      description: "Our dedicated team is here to assist you anytime. for your peace of mind."
    }
  ];

  return (
    <section className="w-full bg-background-accent">
      <div className="max-w-360 mx-auto px-4 sm:px-6 lg:px-8 py-16 lg:py-20">
        <div className="flex flex-col gap-12 lg:gap-16">
          {/* Section Header */}
          <div className="flex flex-col lg:flex-row gap-8 lg:gap-12 items-start">
            <div className="flex flex-col gap-8 lg:gap-20 w-full lg:w-auto">
              <Button
                text="Benefits"
                text_font_size="text-xs"
                text_font_family="Inter"
                text_font_weight="font-normal"
                text_line_height="leading-tight"
                text_color="text-primary-light"
                fill_background_color="bg-secondary-background"
                border_border_radius="rounded-md"
                padding="py-1 px-3"
                text_letter_spacing="1px"
                text_text_transform="uppercase"
                className="w-fit hover:opacity-90"
              />
              
              <div className="hidden lg:block">
                <img
                  src="/images/img_component_1_pink_100_102x82.png"
                  alt="Benefits illustration"
                  className="w-15 h-18.75 lg:w-20.5 lg:h-25.5"
                />
              </div>
            </div>

            <div className="flex-1 space-y-8">
              <h2 className="text-3xl sm:text-4xl lg:text-4xl font-[Roboto Serif] font-normal leading-4xl text-text-primary">
                Flow Diagram
              </h2>
              
              <p className="text-base font-[Inter] font-normal leading-xl text-text-muted max-w-2xl">
                SecureLife Coverage offers you peace of mind with tax-free payouts. Enjoy the flexibility of payment options tailored to your needs.
              </p>
              
              <Button
                text="Contact Us"
                text_font_size="text-base"
                text_font_family="Inter"
                text_font_weight="font-normal"
                text_line_height="leading-base"
                text_color="text-primary-foreground"
                fill_background_color="bg-primary-background"
                border_border_radius="rounded-sm"
                padding="py-3 px-6"
                className="hover:opacity-90 focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Benefits Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-4">
            {benefits?.map((benefit, index) => (
              <div key={index} className="flex flex-col gap-6 max-w-360">
                <div className="w-12 h-12">
                  <img
                    src={benefit?.icon}
                    alt=""
                    className="w-full h-full"
                  />
                </div>
                
                <div className="space-y-3">
                  <h3 className="text-xl font-[Roboto Serif] font-normal leading-xl text-text-primary">
                    {benefit?.title}
                  </h3>
                  
                  <p className="text-base font-[Inter] font-normal leading-xl text-text-muted">
                    {benefit?.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default BenefitsSection;