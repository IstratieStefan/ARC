import React from 'react';
import { motion } from 'framer-motion';

interface HeroProps {
  title: string;
  subtitle: string;
  image: string;
  ctaText?: string;
  ctaLink?: string;
  secondaryCtaText?: string;
  secondaryCtaLink?: string;
}

const Hero: React.FC<HeroProps> = ({
  title,
  subtitle,
  image,
  ctaText,
  ctaLink,
  secondaryCtaText,
  secondaryCtaLink,
}) => {
  return (
    <section className="relative h-screen min-h-[600px] flex items-center overflow-hidden">
      {/* Background Image */}
      <div className="absolute inset-0 z-0">
        <img
          src={image}
          alt="ARC"
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-black bg-opacity-50"></div>
      </div>

      {/* Content */}
      <div className="container-custom relative z-10 pt-20">
        <div className="max-w-3xl">
          <motion.h1 
            className="heading-1 text-white mb-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            {title}
          </motion.h1>
          
          <motion.p 
            className="text-xl text-gray-200 mb-8"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            {subtitle}
          </motion.p>
          
          <motion.div 
            className="flex flex-wrap gap-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
          >
            {ctaText && ctaLink && (
              <a href={ctaLink} className="btn-primary">
                {ctaText}
              </a>
            )}
            
            {secondaryCtaText && secondaryCtaLink && (
              <a href={secondaryCtaLink} className="btn-outline border-white text-white hover:bg-white hover:text-gray-900">
                {secondaryCtaText}
              </a>
            )}
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default Hero;