import React from 'react';
import { Helmet } from 'react-helmet';
import Header from '../../components/common/Header';
import Footer from '../../components/common/Footer';
import HeroSection from './HeroSection';
import WhyChooseUsSection from './WhyChooseUsSection';
import BenefitsSection from './BenefitsSection';
import ArticlesSection from './ArticlesSection';

const Homepage = () => {
  return (
    <>
      <Helmet>
        <title>Quick & Affordable Insurance Policies | InsureGuard Pro</title>
        <meta 
          name="description" 
          content="Get instant quotes for life, health, home & vehicle insurance. Trusted by thousands with 24/7 support, competitive rates & quick claim processing." 
        />
        <meta property="og:title" content="Quick & Affordable Insurance Policies | InsureGuard Pro" />
        <meta property="og:description" content="Get instant quotes for life, health, home & vehicle insurance. Trusted by thousands with 24/7 support, competitive rates & quick claim processing." />
      </Helmet>

      <div className="min-h-screen bg-secondary-background">
        <Header />
        
        <main>
          <HeroSection />
          <WhyChooseUsSection />
          {/* <BenefitsSection />
          <ArticlesSection /> */}
        </main>

        <Footer />
      </div>
    </>
  );
};

export default Homepage;