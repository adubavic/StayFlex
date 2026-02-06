import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Mail, 
  Phone, 
  MapPin, 
  Clock, 
  Send,
  MessageSquare,
  Headphones,
  CheckCircle2,
  Loader2
} from 'lucide-react';
import { toast } from 'sonner';

const ContactPage = () => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1500));
    
    setIsSubmitting(false);
    setIsSubmitted(true);
    toast.success('Message sent successfully! We\'ll get back to you soon.');
  };

  const contactInfo = [
    {
      icon: Mail,
      title: 'Email Us',
      details: ['hello@stayflex.com', 'support@stayflex.com'],
      description: 'We typically respond within 24 hours',
    },
    {
      icon: Phone,
      title: 'Call Us',
      details: ['+1 (555) 123-4567', '+1 (555) 987-6543'],
      description: 'Mon-Fri from 9am to 6pm EST',
    },
    {
      icon: MapPin,
      title: 'Visit Us',
      details: ['123 Experience Avenue', 'New York, NY 10001'],
      description: 'By appointment only',
    },
    {
      icon: Clock,
      title: 'Business Hours',
      details: ['Monday - Friday: 9am - 6pm', 'Saturday: 10am - 4pm'],
      description: 'Closed on Sundays and holidays',
    },
  ];

  const quickLinks = [
    { title: 'Help Center', description: 'Find answers to common questions', href: '/help' },
    { title: 'Track Order', description: 'Check your voucher status', href: '/my-vouchers' },
    { title: 'Partner With Us', description: 'List your property', href: '#' },
    { title: 'Press Inquiries', description: 'Media and press contacts', href: '#' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-amber-500 to-orange-600 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <Badge className="bg-white/20 text-white border-white/30 mb-4">
              <MessageSquare className="w-3 h-3 mr-1" />
              Get in Touch
            </Badge>
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              We're Here to Help
            </h1>
            <p className="text-xl text-white/90">
              Have a question or need assistance? Our friendly support team is 
              ready to help you with anything you need.
            </p>
          </div>
        </div>
      </section>

      {/* Contact Info Cards */}
      <section className="py-16 -mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {contactInfo.map((item) => (
              <Card key={item.title} className="hover:shadow-lg transition-shadow">
                <CardContent className="p-6">
                  <div className="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center mb-4">
                    <item.icon className="w-6 h-6 text-amber-600" />
                  </div>
                  <h3 className="font-semibold text-lg mb-2">{item.title}</h3>
                  {item.details.map((detail, index) => (
                    <p key={index} className="text-gray-900">{detail}</p>
                  ))}
                  <p className="text-sm text-gray-500 mt-2">{item.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Contact Form Section */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            {/* Form */}
            <div>
              <Badge className="mb-4 bg-amber-100 text-amber-700">
                Send a Message
              </Badge>
              <h2 className="text-3xl font-bold mb-4">Get in Touch</h2>
              <p className="text-gray-600 mb-8">
                Fill out the form below and we'll get back to you as soon as possible.
              </p>

              {isSubmitted ? (
                <Card className="bg-green-50 border-green-200">
                  <CardContent className="p-8 text-center">
                    <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <CheckCircle2 className="w-8 h-8 text-green-600" />
                    </div>
                    <h3 className="text-xl font-semibold text-green-800 mb-2">
                      Message Sent!
                    </h3>
                    <p className="text-green-700">
                      Thank you for reaching out. We'll get back to you within 24 hours.
                    </p>
                  </CardContent>
                </Card>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="name">Full Name</Label>
                      <Input
                        id="name"
                        placeholder="John Doe"
                        value={formData.name}
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        required
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="email">Email Address</Label>
                      <Input
                        id="email"
                        type="email"
                        placeholder="john@example.com"
                        value={formData.email}
                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                        required
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="subject">Subject</Label>
                    <Input
                      id="subject"
                      placeholder="How can we help?"
                      value={formData.subject}
                      onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="message">Message</Label>
                    <Textarea
                      id="message"
                      placeholder="Tell us more about your inquiry..."
                      rows={5}
                      value={formData.message}
                      onChange={(e) => setFormData({ ...formData, message: e.target.value })}
                      required
                    />
                  </div>
                  <Button 
                    type="submit" 
                    className="w-full bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700"
                    disabled={isSubmitting}
                  >
                    {isSubmitting ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Sending...
                      </>
                    ) : (
                      <>
                        <Send className="w-4 h-4 mr-2" />
                        Send Message
                      </>
                    )}
                  </Button>
                </form>
              )}
            </div>

            {/* Support Info */}
            <div>
              <Badge className="mb-4 bg-amber-100 text-amber-700">
                <Headphones className="w-3 h-3 mr-1" />
                Support Options
              </Badge>
              <h2 className="text-3xl font-bold mb-4">Other Ways to Reach Us</h2>
              <p className="text-gray-600 mb-8">
                Choose the option that works best for you. We're here to help!
              </p>

              <div className="space-y-4">
                {quickLinks.map((link) => (
                  <Card key={link.title} className="hover:shadow-md transition-shadow cursor-pointer">
                    <CardContent className="p-4 flex items-center justify-between">
                      <div>
                        <h3 className="font-semibold">{link.title}</h3>
                        <p className="text-sm text-gray-500">{link.description}</p>
                      </div>
                      <Button variant="ghost" size="sm">
                        Learn More
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>

              <div className="mt-8 p-6 bg-amber-50 rounded-xl">
                <h3 className="font-semibold text-lg mb-2 text-amber-900">
                  Need Immediate Help?
                </h3>
                <p className="text-amber-800 mb-4">
                  For urgent inquiries about bookings or vouchers, please call our 
                  dedicated support line.
                </p>
                <Button variant="outline" className="border-amber-500 text-amber-700 hover:bg-amber-100">
                  <Phone className="w-4 h-4 mr-2" />
                  +1 (555) 123-4567
                </Button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Map Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold mb-2">Visit Our Office</h2>
            <p className="text-gray-600">
              We're located in the heart of New York City
            </p>
          </div>
          <div className="relative h-96 bg-gray-200 rounded-2xl overflow-hidden">
            {/* Placeholder for map - in production, integrate Google Maps or similar */}
            <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-gray-100 to-gray-200">
              <div className="text-center">
                <MapPin className="w-12 h-12 text-amber-500 mx-auto mb-4" />
                <p className="text-lg font-semibold">StayFlex Headquarters</p>
                <p className="text-gray-600">123 Experience Avenue</p>
                <p className="text-gray-600">New York, NY 10001</p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default ContactPage;
