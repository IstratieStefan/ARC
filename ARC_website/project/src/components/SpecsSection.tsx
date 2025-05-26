import React from 'react';
import { motion } from 'framer-motion';

interface SpecCategory {
  title: string;
  items: {
    name: string;
    value: string;
  }[];
}

interface SpecsSectionProps {
  categories: SpecCategory[];
  image: string;
}

const SpecsSection: React.FC<SpecsSectionProps> = ({ categories, image }) => {
  return (
    <section className="section bg-gray-50" id="specs">
      <div className="container-custom">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6 }}
          >
            <img 
              src={image} 
              alt="ARC Device"
              className="w-full max-w-md mx-auto rounded-[30px] shadow-lg"
            />
          </motion.div>
          
          <div>
            <h2 className="heading-2 mb-8">Technical Specifications</h2>
            
            <div className="space-y-8">
              {categories.map((category, categoryIndex) => (
                <motion.div 
                  key={categoryIndex}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.5, delay: categoryIndex * 0.1 }}
                >
                  <h3 className="heading-3 mb-4">{category.title}</h3>
                  <div className="space-y-2">
                    {category.items.map((item, itemIndex) => (
                      <div 
                        key={itemIndex} 
                        className="flex justify-between py-2 border-b border-gray-200 last:border-0"
                      >
                        <span className="font-medium text-gray-700">{item.name}</span>
                        <span className="text-gray-900">{item.value}</span>
                      </div>
                    ))}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default SpecsSection;