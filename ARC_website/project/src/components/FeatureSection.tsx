import React from 'react';
import { motion } from 'framer-motion';
import LockOpenIcon from '@mui/icons-material/LockOpen';
import TrackChangesIcon from '@mui/icons-material/TrackChanges';
import SecurityIcon from '@mui/icons-material/Security';
import BuildIcon from '@mui/icons-material/Build';
import CodeIcon from '@mui/icons-material/Code';
import AppsIcon from '@mui/icons-material/Apps';

const iconMap = {
  LockOpen: LockOpenIcon,
  TrackChanges: TrackChangesIcon,
  Security: SecurityIcon,
  Build: BuildIcon,
  Code: CodeIcon,
  Apps: AppsIcon,
};

interface Feature {
  icon: string;
  title: string;
  description: string;
}

interface FeatureSectionProps {
  title: string;
  subtitle?: string;
  features: Feature[];
}

const FeatureSection: React.FC<FeatureSectionProps> = ({ title, subtitle, features }) => {
  return (
    <section className="section bg-white" id="features">
      <div className="container-custom">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="heading-2 mb-4">{title}</h2>
          {subtitle && <p className="text-xl text-gray-600">{subtitle}</p>}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
              <motion.div
                  key={index}
                  className="card p-6"
                  initial={{opacity: 0, y: 20}}
                  whileInView={{opacity: 1, y: 0}}
                  viewport={{once: true}}
                  transition={{duration: 0.5, delay: index * 0.1}}
              >
                <div className="w-12 h-12 bg-accent/10 rounded-lg flex items-center justify-center text-accent mb-6">
                  {(() => {
                    const Icon = iconMap[feature.icon as keyof typeof iconMap];
                    return Icon ? <Icon fontSize="large"/> : null;
                  })()}
                </div>
                <h3 className="text-xl font-semibold mb-3">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default FeatureSection;