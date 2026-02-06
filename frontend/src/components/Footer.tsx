import { Link } from 'react-router-dom';
import { Gift, Mail, Phone, MapPin, Instagram, Facebook, Twitter } from 'lucide-react';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  const footerLinks = {
    company: [
      { name: 'About Us', href: '/about' },
      { name: 'How It Works', href: '/help' },
      { name: 'Careers', href: '#' },
      { name: 'Press', href: '#' },
    ],
    support: [
      { name: 'Help Center', href: '/help' },
      { name: 'Contact Us', href: '/contact' },
      { name: 'Terms of Service', href: '#' },
      { name: 'Privacy Policy', href: '#' },
    ],
    partners: [
      { name: 'List Your Property', href: '#' },
      { name: 'Partner Login', href: '#' },
      { name: 'Affiliate Program', href: '#' },
    ],
  };

  return (
    <footer className="bg-gray-900 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8">
          {/* Brand */}
          <div className="lg:col-span-2">
            <Link to="/" className="flex items-center space-x-2 mb-4">
              <div className="w-10 h-10 bg-gradient-to-br from-amber-500 to-orange-600 rounded-lg flex items-center justify-center">
                <Gift className="w-6 h-6 text-white" />
              </div>
              <span className="text-2xl font-bold">StayFlex</span>
            </Link>
            <p className="text-gray-400 mb-6 max-w-sm">
              Gift unforgettable experiences. From romantic getaways to adventure escapes, 
              create memories that last a lifetime.
            </p>
            <div className="flex space-x-4">
              <a href="#" className="w-10 h-10 bg-gray-800 rounded-full flex items-center justify-center hover:bg-amber-600 transition-colors">
                <Instagram className="w-5 h-5" />
              </a>
              <a href="#" className="w-10 h-10 bg-gray-800 rounded-full flex items-center justify-center hover:bg-amber-600 transition-colors">
                <Facebook className="w-5 h-5" />
              </a>
              <a href="#" className="w-10 h-10 bg-gray-800 rounded-full flex items-center justify-center hover:bg-amber-600 transition-colors">
                <Twitter className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Company Links */}
          <div>
            <h3 className="font-semibold text-lg mb-4">Company</h3>
            <ul className="space-y-3">
              {footerLinks.company.map((link) => (
                <li key={link.name}>
                  {link.href.startsWith('/') ? (
                    <Link to={link.href} className="text-gray-400 hover:text-white transition-colors">
                      {link.name}
                    </Link>
                  ) : (
                    <a href={link.href} className="text-gray-400 hover:text-white transition-colors">
                      {link.name}
                    </a>
                  )}
                </li>
              ))}
            </ul>
          </div>

          {/* Support Links */}
          <div>
            <h3 className="font-semibold text-lg mb-4">Support</h3>
            <ul className="space-y-3">
              {footerLinks.support.map((link) => (
                <li key={link.name}>
                  {link.href.startsWith('/') ? (
                    <Link to={link.href} className="text-gray-400 hover:text-white transition-colors">
                      {link.name}
                    </Link>
                  ) : (
                    <a href={link.href} className="text-gray-400 hover:text-white transition-colors">
                      {link.name}
                    </a>
                  )}
                </li>
              ))}
            </ul>
          </div>

          {/* Partners Links */}
          <div>
            <h3 className="font-semibold text-lg mb-4">Partners</h3>
            <ul className="space-y-3">
              {footerLinks.partners.map((link) => (
                <li key={link.name}>
                  {link.href.startsWith('/') ? (
                    <Link to={link.href} className="text-gray-400 hover:text-white transition-colors">
                      {link.name}
                    </Link>
                  ) : (
                    <a href={link.href} className="text-gray-400 hover:text-white transition-colors">
                      {link.name}
                    </a>
                  )}
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Contact Info */}
        <div className="border-t border-gray-800 mt-12 pt-8">
          <div className="flex flex-wrap justify-center gap-6 text-gray-400 text-sm">
            <div className="flex items-center">
              <Mail className="w-4 h-4 mr-2" />
              <span>hello@stayflex.com</span>
            </div>
            <div className="flex items-center">
              <Phone className="w-4 h-4 mr-2" />
              <span>+1 (555) 123-4567</span>
            </div>
            <div className="flex items-center">
              <MapPin className="w-4 h-4 mr-2" />
              <span>123 Experience Ave, New York, NY</span>
            </div>
          </div>
        </div>

        {/* Copyright */}
        <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400 text-sm">
          <p>&copy; {currentYear} StayFlex. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
