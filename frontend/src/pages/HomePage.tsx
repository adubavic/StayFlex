import { Link } from 'react-router-dom';
import { usePackages } from '@/hooks/usePackages';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Gift, 
  Calendar, 
  MapPin, 
  Sparkles,
  ArrowRight,
  Check,
  Heart
} from 'lucide-react';

const HomePage = () => {
  const { data: featuredPackages, isLoading } = usePackages({ featured_only: true });

  const howItWorks = [
    {
      icon: Gift,
      title: 'Choose a Package',
      description: 'Browse our curated collection of experience packages for every occasion.',
    },
    {
      icon: Calendar,
      title: 'Book Your Stay',
      description: 'Select your dates and choose from our partner properties.',
    },
    {
      icon: Sparkles,
      title: 'Enjoy the Experience',
      description: 'Create unforgettable memories at your chosen destination.',
    },
  ];

  const benefits = [
    'Access to 5,000+ partner properties',
    'Flexible booking dates',
    'Best price guarantee',
    'Free cancellation up to 48 hours',
    '24/7 customer support',
    'Gift wrapping available',
  ];

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative h-[80vh] flex items-center">
        {/* Background Image */}
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: 'url(/images/hero-hotel.jpg)' }}
        >
          <div className="absolute inset-0 bg-gradient-to-r from-black/70 via-black/50 to-transparent" />
        </div>

        {/* Content */}
        <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-2xl">
            <Badge className="mb-4 bg-amber-500/20 text-amber-300 border-amber-500/30">
              <Sparkles className="w-3 h-3 mr-1" />
              Gift Unforgettable Experiences
            </Badge>
            <h1 className="text-4xl md:text-6xl font-bold text-white mb-6 leading-tight">
              Give the Gift of{' '}
              <span className="bg-gradient-to-r from-amber-400 to-orange-400 bg-clip-text text-transparent">
                Amazing Stays
              </span>
            </h1>
            <p className="text-xl text-gray-200 mb-8">
              From romantic getaways to adventure escapes, our experience packages 
              let your loved ones choose their perfect stay from thousands of properties.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link to="/packages">
                <Button size="lg" className="bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700 text-lg px-8">
                  Explore Packages
                  <ArrowRight className="ml-2 w-5 h-5" />
                </Button>
              </Link>
              <Link to="/register">
                <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10 text-lg px-8">
                  Get Started
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Packages Section */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Featured Experience Packages
            </h2>
            <p className="text-gray-600 text-lg max-w-2xl mx-auto">
              Our most popular gift packages, carefully curated for every occasion
            </p>
          </div>

          {isLoading ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {[1, 2, 3].map((i) => (
                <Card key={i} className="animate-pulse">
                  <div className="h-64 bg-gray-200" />
                  <CardContent className="p-6">
                    <div className="h-6 bg-gray-200 rounded mb-2" />
                    <div className="h-4 bg-gray-200 rounded w-2/3" />
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {featuredPackages?.map((pkg: any) => (
                <Link key={pkg.id} to={`/packages/${pkg.slug}`}>
                  <Card className="overflow-hidden group cursor-pointer hover:shadow-xl transition-shadow">
                    <div className="relative h-64 overflow-hidden">
                      <img
                        src={pkg.image_url || '/images/hero-hotel.jpg'}
                        alt={pkg.name}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                      />
                      <div className="absolute top-4 left-4">
                        <Badge className="bg-white/90 text-gray-900">
                          <Heart className="w-3 h-3 mr-1 text-red-500" />
                          {pkg.rating} ({pkg.review_count})
                        </Badge>
                      </div>
                      {pkg.discount_percentage > 0 && (
                        <div className="absolute top-4 right-4">
                          <Badge className="bg-red-500 text-white">
                            Save {pkg.discount_percentage}%
                          </Badge>
                        </div>
                      )}
                    </div>
                    <CardContent className="p-6">
                      <div className="flex items-center text-sm text-gray-500 mb-2">
                        <MapPin className="w-4 h-4 mr-1" />
                        {pkg.city}, {pkg.state}
                      </div>
                      <h3 className="text-xl font-semibold mb-2">{pkg.name}</h3>
                      <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                        {pkg.short_description}
                      </p>
                      <div className="flex items-center justify-between">
                        <div>
                          <span className="text-2xl font-bold text-amber-600">
                            ₦{(pkg.base_price_kobo / 100).toLocaleString()}
                          </span>
                          <span className="text-gray-400 text-sm line-through ml-2">
                            ₦{(pkg.original_value_kobo / 100).toLocaleString()}
                          </span>
                        </div>
                        <span className="text-sm text-gray-500">
                          {pkg.nights_included} nights
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </div>
          )}

          <div className="text-center mt-12">
            <Link to="/packages">
              <Button variant="outline" size="lg" className="border-amber-500 text-amber-600 hover:bg-amber-50">
                View All Packages
                <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">How It Works</h2>
            <p className="text-gray-600 text-lg max-w-2xl mx-auto">
              Three simple steps to gift an unforgettable experience
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {howItWorks.map((step, index) => (
              <div key={step.title} className="text-center">
                <div className="w-16 h-16 bg-gradient-to-br from-amber-500 to-orange-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <step.icon className="w-8 h-8 text-white" />
                </div>
                <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4 font-bold text-gray-600">
                  {index + 1}
                </div>
                <h3 className="text-xl font-semibold mb-3">{step.title}</h3>
                <p className="text-gray-600">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 bg-gradient-to-br from-amber-500 to-orange-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold mb-6">
                Why Choose StayFlex?
              </h2>
              <p className="text-white/90 text-lg mb-8">
                We partner with the best hotels and resorts to bring you 
                unforgettable experiences at unbeatable prices.
              </p>
              <ul className="space-y-4">
                {benefits.map((benefit) => (
                  <li key={benefit} className="flex items-center">
                    <div className="w-6 h-6 bg-white/20 rounded-full flex items-center justify-center mr-3">
                      <Check className="w-4 h-4" />
                    </div>
                    {benefit}
                  </li>
                ))}
              </ul>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <img
                src="/images/package-spa.jpg"
                alt="Spa experience"
                className="rounded-2xl w-full h-48 object-cover"
              />
              <img
                src="/images/package-romantic.jpg"
                alt="Romantic getaway"
                className="rounded-2xl w-full h-48 object-cover mt-8"
              />
              <img
                src="/images/package-adventure.jpg"
                alt="Adventure"
                className="rounded-2xl w-full h-48 object-cover -mt-8"
              />
              <img
                src="/images/package-city.jpg"
                alt="City break"
                className="rounded-2xl w-full h-48 object-cover"
              />
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Ready to Give an Unforgettable Gift?
          </h2>
          <p className="text-gray-600 text-lg mb-8">
            Join thousands of happy customers who have gifted amazing experiences 
            to their loved ones.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/packages">
              <Button size="lg" className="bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700 text-lg px-8">
                Browse Packages
                <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
            </Link>
            <Link to="/register">
              <Button size="lg" variant="outline" className="text-lg px-8">
                Create Account
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
