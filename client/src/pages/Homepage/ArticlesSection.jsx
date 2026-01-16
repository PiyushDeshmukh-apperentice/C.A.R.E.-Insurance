import React from 'react';
import Button from '../../components/ui/Button';

const ArticlesSection = () => {
  const articles = [
    {
      image: "/images/img_68c0adb784571f5.png",
      category: "Insurance",
      title: "Understanding your insurance needs",
      description: "Explore how to choose the right coverage for you.",
      link: "/articles/understanding-insurance-needs"
    },
    {
      image: "/images/img_68b3175c3f09d20.png", 
      category: "Tips",
      title: "Tips for homeowners insurance",
      description: "Essential tips to ensure your home is properly covered.",
      link: "/articles/homeowners-insurance-tips"
    },
    {
      image: "/images/img_68b31996d67478a.png",
      categories: ["Corporate", "Finance", "Tax"],
      title: "Life Insurance basics explained", 
      description: "Explore how to choose the right coverage for you.",
      link: "/articles/life-insurance-basics"
    }
  ];

  return (
    <section className="w-full bg-secondary-background">
      <div className="max-w-360 mx-auto px-4 sm:px-6 lg:px-8 py-16 lg:py-20">
        <div className="flex flex-col gap-12 lg:gap-16 items-center">
          {/* Section Header */}
          <div className="text-center space-y-6 max-w-4xl">
            <Button
              text="Articles"
              text_font_size="text-xs"
              text_font_family="Inter"
              text_font_weight="font-normal"
              text_line_height="leading-tight"
              text_color="text-primary-light"
              fill_background_color="bg-background-accent"
              border_border_radius="rounded-md"
              padding="py-1 px-3"
              text_letter_spacing="1px"
              text_text_transform="uppercase"
              className="mx-auto hover:opacity-90"
            />
            
            <h2 className="text-3xl sm:text-4xl lg:text-4xl font-[Roboto Serif] font-normal leading-4xl text-text-primary">
              Insurance insights and tips
            </h2>
          </div>

          {/* Articles Grid */}
          <div className="w-full">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {articles?.map((article, index) => (
                <article key={index} className="bg-background-footer rounded-sm overflow-hidden">
                  <div className="aspect-4/3 w-full">
                    <img
                      src={article?.image}
                      alt={article?.title}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  
                  <div className="p-6 space-y-6">
                    <div className="space-y-3">
                      {/* Category Tags */}
                      <div className="flex flex-wrap gap-2">
                        {article?.category ? (
                          <Button
                            text={article?.category}
                            text_font_size="text-xs"
                            text_font_family="Inter"
                            text_font_weight="font-normal"
                            text_line_height="leading-tight"
                            text_color="text-text-primary"
                            fill_background_color="bg-background-light"
                            border_border_radius="rounded-xs"
                            padding="py-1.5 px-2"
                            text_text_transform="capitalize"
                            className="hover:opacity-90"
                          />
                        ) : (
                          article?.categories?.map((cat, catIndex) => (
                            <Button
                              key={catIndex}
                              text={cat}
                              text_font_size="text-xs"
                              text_font_family="Inter"
                              text_font_weight="font-normal"
                              text_line_height="leading-tight"
                              text_color="text-text-primary"
                              fill_background_color="bg-background-light"
                              border_border_radius="rounded-xs"
                              padding="py-1.5 px-2"
                              text_text_transform="capitalize"
                              className="hover:opacity-90"
                            />
                          ))
                        )}
                      </div>
                      
                      <h3 className="text-xl font-[Roboto Serif] font-normal leading-xl text-text-primary">
                        {article?.title}
                      </h3>
                      
                      <p className="text-base font-[Inter] font-normal leading-xl text-text-muted">
                        {article?.description}
                      </p>
                    </div>
                    
                    <div>
                      <a 
                        href={article?.link}
                        className="text-base font-[Inter] font-normal leading-base tracking-wider uppercase text-text-primary hover:text-primary-background transition-colors duration-200"
                      >
                        Learn more
                      </a>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          </div>

          {/* View More Button */}
          <Button
            text="View more"
            text_font_size="text-base"
            text_font_family="Inter"
            text_font_weight="font-normal"
            text_line_height="leading-base"
            text_color="text-primary-background"
            fill_background_color="bg-background-accent"
            border_border_radius="rounded-sm"
            border_border="1px solid #0c204b"
            padding="py-3 px-6"
            className="border border-primary-background hover:bg-primary-background hover:text-primary-foreground transition-colors duration-200"
          />
        </div>
      </div>
    </section>
  );
};

export default ArticlesSection;