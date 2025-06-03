import React, { useState, useEffect } from 'react';
import html2canvas from 'html2canvas';

const Navbar: React.FC = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isLightUnderlay, setIsLightUnderlay] = useState(true);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  // Handle scroll
  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 10);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Sample pixels under navbar when not scrolled
  useEffect(() => {
    if (!isScrolled) {
      html2canvas(document.body, {
        useCORS: true,
        backgroundColor: null,
        scale: 0.5,
      }).then(canvas => {
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        const navHeight = 80;
        const sampleWidth = canvas.width;
        const sampleHeight = Math.min(navHeight, canvas.height);

        let r = 0, g = 0, b = 0, count = 0;

        for (let y = 0; y < sampleHeight; y += 10) {
          for (let x = 0; x < sampleWidth; x += 20) {
            const [pr, pg, pb] = ctx.getImageData(x, y, 1, 1).data;
            r += pr;
            g += pg;
            b += pb;
            count++;
          }
        }

        if (count > 0) {
          const avgR = r / count;
          const avgG = g / count;
          const avgB = b / count;
          const brightness = (avgR * 299 + avgG * 587 + avgB * 114) / 1000;
          setIsLightUnderlay(brightness > 150);
        }
      });
    }
  }, [isScrolled]);

  const navLinks = [
    { name: 'Home', href: '/' },
    { name: 'Download', href: '/download' },
    { name: 'App Store', href: '/app-store' },
    { name: 'ARC Connect', href: '/arc-connect' },
    { name: 'Gallery', href: '/gallery' },
    { name: 'Docs', href: '/docs' },
  ];

  const linkTextClass =
      isScrolled || (!isScrolled && isLightUnderlay)
          ? "text-gray-900 hover:text-accent"
          : "text-white hover:text-accent";

  return (
      <header
          className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
              isScrolled
                  ? 'bg-white/90 backdrop-blur-md shadow-sm'
                  : 'bg-transparent'
          }`}
      >
        <div className="container-custom">
          <div className="flex items-center justify-between h-16 md:h-20">
            <a href="/" className="flex items-center">
              <img
                  src={isScrolled || (!isScrolled && isLightUnderlay) ? "/logo.svg" : "/logo_light.svg"}
                  alt="ARC Logo"
                  className="h-16 w-16 mr-2 transition-all duration-300"
              />
            </a>

            <nav className="hidden md:flex items-center space-x-8">
              {navLinks.map((link) => (
                  <a
                      key={link.name}
                      href={link.href}
                      className={`${linkTextClass} font-medium transition-colors duration-300`}
                  >
                    {link.name}
                  </a>
              ))}
            </nav>

            <button
                className={`md:hidden p-2 focus:outline-none transition-colors duration-300 ${
                    isScrolled || isLightUnderlay ? "text-gray-900" : "text-white"
                }`}
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                aria-label="Toggle menu"
            >
              <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  className="w-6 h-6"
              >
                {isMobileMenuOpen ? (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>

        {isMobileMenuOpen && (
            <div className="md:hidden bg-white shadow-lg animate-fade-in">
              <div className="container-custom py-4">
                <nav className="flex flex-col space-y-4">
                  {navLinks.map((link) => (
                      <a
                          key={link.name}
                          href={link.href}
                          className="text-gray-900 hover:text-accent py-2 font-medium transition-colors duration-300"
                          onClick={() => setIsMobileMenuOpen(false)}
                      >
                        {link.name}
                      </a>
                  ))}
                </nav>
              </div>
            </div>
        )}
      </header>
  );
};

export default Navbar;
