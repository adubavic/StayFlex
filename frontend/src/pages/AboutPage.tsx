import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Gift, 
  Heart, 
  Users, 
  Building2, 
  Star,
  CheckCircle2,
  ArrowRight,
  Sparkles,
  MapPin,
  Shield
} from 'lucide-react';

const AboutPage = () => {
  const stats = [
    { value: '50,000+', label: 'Happy Customers', icon: Users },
    { value: '5,000+', label: 'Partner Properties', icon: Building2 },
    { value: '100,000+', label: 'Experiences Gifted', icon: Gift },
    { value: '4.8/5', label: 'Average Rating', icon: Star },
  ];

  const values = [
    {
      icon: Heart,
      title: 'Memories Over Things',
      description: 'We believe experiences create lasting memories that material gifts simply cannot match.',
    },
    {
      icon: Shield,
      title: 'Trust & Transparency',
      description: 'No hidden fees, no surprises. What you see is what you get, every single time.',
    },
    {
      icon: Sparkles,
      title: 'Quality First',
      description: 'Every partner property is carefully vetted to ensure exceptional experiences.',
    },
    {
      icon: Users,
      title: 'Customer Obsessed',
      description: 'Your satisfaction is our priority. Our support team is here to help, always.',
    },
  ];

  const howItWorks = [
    {
      step: '01',
      title: 'Choose a Package',
      description: 'Browse our curated collection of experience packages. Each package contains multiple experiences within a price range.',
    },
    {
      step: '02',
      title: 'Personalize & Send',
      description: 'Add a personal message and choose how to deliver - instantly via email or as a beautifully packaged physical gift.',
    },
    {
      step: '03',
      title: 'They Choose & Book',
      description: 'The recipient browses all available experiences and books their favorite directly through our platform.',
    },
    {
      step: '04',
      title: 'Create Memories',
      description: 'They enjoy their chosen experience and create memories that last a lifetime.',
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-amber-500 to-orange-600 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <Badge className="bg-white/20 text-white border-white/30 mb-4">
              <Sparkles className="w-3 h-3 mr-1" />
              About StayFlex
            </Badge>
            <h1 className="text-4xl md:text-5xl font-bold mb-6">
              We Believe in the Power of Experiences
            </h1>
            <p className="text-xl text-white/90 mb-8">
              StayFlex is a curated marketplace for hotel experience packages. 
              We connect people with unforgettable stays at the world's finest properties.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link to="/packages">
                <Button size="lg" className="bg-white text-amber-600 hover:bg-white/90">
                  Explore Packages
                  <ArrowRight className="ml-2 w-5 h-5" />
                </Button>
              </Link>
              <Link to="/contact">
                <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10">
                  Contact Us
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 -mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {stats.map((stat) => (
              <Card key={stat.label} className="text-center">
                <CardContent className="p-6">
                  <stat.icon className="w-8 h-8 text-amber-500 mx-auto mb-3" />
                  <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
                  <p className="text-gray-600">{stat.label}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Our Story Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <Badge className="mb-4 bg-amber-100 text-amber-700">
                Our Story
              </Badge>
              <h2 className="text-3xl md:text-4xl font-bold mb-6">
                Creating Memories Since 2020
              </h2>
              <div className="space-y-4 text-gray-600">
                <p>
                  StayFlex was born from a simple idea: the best gifts aren't things, they're experiences. 
                  We started with a mission to help people give the gift of unforgettable memories.
                </p>
                <p>
                  What began as a small collection of boutique hotels has grown into a curated marketplace 
                  featuring thousands of partner properties across the globe. From romantic city escapes 
                  to adventurous mountain retreats, we offer experiences for every taste and occasion.
                </p>
                <p>
                  Our team of travel enthusiasts and hospitality experts carefully vets each property 
                  to ensure that every experience meets our high standards of quality and service.
                </p>
              </div>
              <div className="mt-8 space-y-3">
                {[
                  'Handpicked partner properties',
                  'Flexible booking options',
                  '24/7 customer support',
                  'Best price guarantee',
                ].map((item) => (
                  <div key={item} className="flex items-center">
                    <CheckCircle2 className="w-5 h-5 text-green-500 mr-3" />
                    <span>{item}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="relative">
              <img
                src="/images/about-team.jpg"
                alt="StayFlex Team"
                className="rounded-2xl shadow-xl w-full"
              />
              <div className="absolute -bottom-6 -left-6 bg-white p-4 rounded-xl shadow-lg">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-amber-100 rounded-full flex items-center justify-center">
                    <MapPin className="w-6 h-6 text-amber-600" />
                  </div>
                  <div>
                    <p className="font-semibold">Global Reach</p>
                    <p className="text-sm text-gray-500">50+ Countries</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <Badge className="mb-4 bg-amber-100 text-amber-700">
              How It Works
            </Badge>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Four Simple Steps to Gift Happiness
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Giving the perfect gift has never been easier. Our streamlined process 
              makes it simple to create unforgettable memories.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {howItWorks.map((item) => (
              <div key={item.step} className="relative">
                <div className="text-6xl font-bold text-amber-100 mb-4">
                  {item.step}
                </div>
                <h3 className="text-xl font-semibold mb-3">{item.title}</h3>
                <p className="text-gray-600">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Our Values Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <Badge className="mb-4 bg-amber-100 text-amber-700">
              Our Values
            </Badge>
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              What We Stand For
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Our values guide everything we do, from selecting partner properties 
              to supporting our customers.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {values.map((value) => (
              <Card key={value.title} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center mb-4">
                    <value.icon className="w-6 h-6 text-amber-600" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">{value.title}</h3>
                  <p className="text-gray-600">{value.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-br from-gray-900 to-gray-800 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Ready to Create Unforgettable Memories?
          </h2>
          <p className="text-gray-300 text-lg mb-8">
            Join thousands of happy customers who have gifted amazing experiences 
            to their loved ones. Start exploring our curated collection today.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/packages">
              <Button size="lg" className="bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700">
                Browse Packages
                <ArrowRight className="ml-2 w-5 h-5" />
              </Button>
            </Link>
            <Link to="/help">
              <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10">
                Learn More
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default AboutPage;
