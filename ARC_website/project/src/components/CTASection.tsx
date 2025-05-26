import React from 'react';
import { motion } from 'framer-motion';

interface CTASectionProps {
  title: string;
  subtitle: string;
  buttonText: string;
  buttonLink: string;
  secondaryButtonText?: string;
  secondaryButtonLink?: string;
}

const CTASection: React.FC<CTASectionProps> = ({
  title,
  subtitle,
  buttonText,
  buttonLink,
  secondaryButtonText,
  secondaryButtonLink,
}) => {
  return (
    <section className="section bg-gray-900 text-white">
      <div className="container-custom">
        <motion.div 
          className="text-center max-w-3xl mx-auto"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="heading-2 mb-4">{title}</h2>
          <p className="text-xl text-gray-300 mb-8">{subtitle}</p>
          
          <div className="flex flex-wrap justify-center gap-4">
            <a href={buttonLink} className="btn-primary">
              {buttonText}
            </a>
            
            {secondaryButtonText && secondaryButtonLink && (
              <a href={secondaryButtonLink} className="btn-outline border-white text-white hover:bg-white hover:text-gray-900">
                {secondaryButtonText}
              </a>
            )}
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default CTASection;