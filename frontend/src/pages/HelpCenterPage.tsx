import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { 
  Search, 
  HelpCircle, 
  ShoppingBag, 
  Calendar, 
  CreditCard, 
  Gift, 
  RefreshCw, 
  MessageSquare,
  Phone,
  Mail,
  ChevronRight,
  BookOpen,
  Shield,
  User
} from 'lucide-react';

const HelpCenterPage = () => {
  const [searchQuery, setSearchQuery] = useState('');

  const categories = [
    {
      icon: ShoppingBag,
      title: 'Purchasing',
      description: 'Questions about buying vouchers and packages',
      count: 8,
    },
    {
      icon: Gift,
      title: 'Vouchers',
      description: 'Everything about using your vouchers',
      count: 10,
    },
    {
      icon: Calendar,
      title: 'Bookings',
      description: 'How to book and manage your stays',
      count: 7,
    },
    {
      icon: CreditCard,
      title: 'Payments',
      description: 'Payment methods and billing questions',
      count: 6,
    },
    {
      icon: RefreshCw,
      title: 'Refunds & Cancellations',
      description: 'Our refund and cancellation policies',
      count: 5,
    },
    {
      icon: User,
      title: 'Account',
      description: 'Managing your account settings',
      count: 4,
    },
  ];

  const faqs = [
    {
      category: 'purchasing',
      question: 'How do I purchase an experience package?',
      answer: 'Browse our collection of experience packages, select the one you like, choose the number of nights, and click "Purchase Now". You\'ll be guided through the checkout process where you can pay securely.',
    },
    {
      category: 'purchasing',
      question: 'Can I buy a voucher as a gift?',
      answer: 'Absolutely! All our vouchers make perfect gifts. During checkout, you can choose to send the voucher directly to the recipient via email with a personalized message, or send it to yourself to print and gift in person.',
    },
    {
      category: 'purchasing',
      question: 'How long are vouchers valid for?',
      answer: 'Most vouchers are valid for 12 months from the date of purchase. The exact validity period is clearly displayed on each package page and on your voucher.',
    },
    {
      category: 'vouchers',
      question: 'How do I redeem my voucher?',
      answer: 'Log into your account, go to "My Vouchers", select the voucher you want to redeem, choose your preferred dates, and browse available properties. Once you find a property you like, complete the booking process.',
    },
    {
      category: 'vouchers',
      question: 'Can I use my voucher at any property?',
      answer: 'Your voucher can be redeemed at any partner property that matches the package criteria (location, property type, etc.). When redeeming, you\'ll see all eligible properties for your specific voucher.',
    },
    {
      category: 'vouchers',
      question: 'What if I lose my voucher code?',
      answer: 'Don\'t worry! Your voucher codes are always available in your account under "My Vouchers". You can also contact our support team if you need assistance.',
    },
    {
      category: 'vouchers',
      question: 'Can I extend my voucher validity?',
      answer: 'In most cases, yes! Contact our support team before your voucher expires and we can help extend the validity period for a small fee.',
    },
    {
      category: 'bookings',
      question: 'How far in advance should I book?',
      answer: 'We recommend booking at least 2-4 weeks in advance for the best availability. However, you can book as far in advance as the property\'s availability allows.',
    },
    {
      category: 'bookings',
      question: 'Can I modify my booking dates?',
      answer: 'Yes, you can modify your booking dates up to 48 hours before your scheduled check-in, subject to property availability. Contact our support team to make changes.',
    },
    {
      category: 'bookings',
      question: 'What happens if the property cancels my booking?',
      answer: 'If a property cancels your booking, we\'ll immediately notify you and help you find an alternative property or provide a full refund, whichever you prefer.',
    },
    {
      category: 'payments',
      question: 'What payment methods do you accept?',
      answer: 'We accept all major credit cards (Visa, Mastercard, American Express), Paystack, and bank transfers. All payments are processed securely.',
    },
    {
      category: 'payments',
      question: 'Is my payment information secure?',
      answer: 'Yes! We use industry-standard SSL encryption and never store your full credit card details. All payments are processed through secure, PCI-compliant payment gateways.',
    },
    {
      category: 'refunds',
      question: 'What is your cancellation policy?',
      answer: 'You can cancel your voucher within 14 days of purchase for a full refund, provided it hasn\'t been used. After 14 days, vouchers are non-refundable but remain valid for the full validity period.',
    },
    {
      category: 'refunds',
      question: 'How do I request a refund?',
      answer: 'To request a refund, contact our support team with your voucher code and reason for the refund. We\'ll review your request and process eligible refunds within 5-7 business days.',
    },
    {
      category: 'account',
      question: 'How do I create an account?',
      answer: 'Click "Get Started" or "Sign Up" on our homepage, fill in your details, and verify your email address. It takes less than a minute!',
    },
    {
      category: 'account',
      question: 'How do I reset my password?',
      answer: 'Click "Forgot Password" on the login page, enter your email address, and we\'ll send you a password reset link. Follow the instructions to create a new password.',
    },
  ];

  const filteredFaqs = searchQuery
    ? faqs.filter(
        (faq) =>
          faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
          faq.answer.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : faqs;

  const popularArticles = [
    { title: 'How to Redeem Your Voucher', views: '12.5k views' },
    { title: 'Booking Cancellation Policy', views: '8.2k views' },
    { title: 'Gift Voucher Guide', views: '7.8k views' },
    { title: 'Payment Methods Explained', views: '6.1k views' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-amber-500 to-orange-600 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto">
            <Badge className="bg-white/20 text-white border-white/30 mb-4">
              <HelpCircle className="w-3 h-3 mr-1" />
              Help Center
            </Badge>
            <h1 className="text-4xl md:text-5xl font-bold mb-4">
              How Can We Help?
            </h1>
            <p className="text-xl text-white/90 mb-8">
              Find answers to common questions or get in touch with our support team.
            </p>
            <div className="relative max-w-xl mx-auto">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <Input
                placeholder="Search for answers..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 h-12 bg-white text-gray-900"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Categories Section */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-2xl font-bold mb-8 text-center">
            Browse by Category
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {categories.map((category) => (
              <Card 
                key={category.title} 
                className="hover:shadow-lg transition-shadow cursor-pointer group"
              >
                <CardContent className="p-6">
                  <div className="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center mb-4 group-hover:bg-amber-200 transition-colors">
                    <category.icon className="w-6 h-6 text-amber-600" />
                  </div>
                  <h3 className="font-semibold text-lg mb-1">{category.title}</h3>
                  <p className="text-gray-600 text-sm mb-3">{category.description}</p>
                  <div className="flex items-center text-amber-600 text-sm">
                    <span>{category.count} articles</span>
                    <ChevronRight className="w-4 h-4 ml-1" />
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-16 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-2xl font-bold mb-8 text-center">
            {searchQuery ? 'Search Results' : 'Frequently Asked Questions'}
          </h2>
          
          {filteredFaqs.length === 0 ? (
            <div className="text-center py-12">
              <HelpCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold mb-2">No results found</h3>
              <p className="text-gray-600 mb-4">
                Try different keywords or contact our support team.
              </p>
              <Link to="/contact">
                <Button>Contact Support</Button>
              </Link>
            </div>
          ) : (
            <Accordion type="single" collapsible className="w-full">
              {filteredFaqs.map((faq, index) => (
                <AccordionItem key={index} value={`item-${index}`}>
                  <AccordionTrigger className="text-left">
                    {faq.question}
                  </AccordionTrigger>
                  <AccordionContent className="text-gray-600">
                    {faq.answer}
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          )}
        </div>
      </section>

      {/* Popular Articles */}
      {!searchQuery && (
        <section className="py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Popular Articles */}
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <BookOpen className="w-5 h-5 text-amber-600" />
                    <h3 className="font-semibold">Popular Articles</h3>
                  </div>
                  <div className="space-y-4">
                    {popularArticles.map((article) => (
                      <div 
                        key={article.title} 
                        className="flex items-center justify-between py-2 border-b last:border-0 cursor-pointer hover:text-amber-600 transition-colors"
                      >
                        <span className="text-sm">{article.title}</span>
                        <span className="text-xs text-gray-500">{article.views}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Quick Support */}
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <MessageSquare className="w-5 h-5 text-amber-600" />
                    <h3 className="font-semibold">Need More Help?</h3>
                  </div>
                  <p className="text-gray-600 text-sm mb-4">
                    Can't find what you're looking for? Our support team is here to help.
                  </p>
                  <div className="space-y-3">
                    <Link to="/contact">
                      <Button variant="outline" className="w-full justify-start">
                        <Mail className="w-4 h-4 mr-2" />
                        Send us an email
                      </Button>
                    </Link>
                    <Button variant="outline" className="w-full justify-start">
                      <Phone className="w-4 h-4 mr-2" />
                      Call +1 (555) 123-4567
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Trust Badge */}
              <Card className="bg-gradient-to-br from-amber-50 to-orange-50">
                <CardContent className="p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <Shield className="w-5 h-5 text-amber-600" />
                    <h3 className="font-semibold">Your Satisfaction Guaranteed</h3>
                  </div>
                  <p className="text-gray-600 text-sm mb-4">
                    We're committed to providing exceptional experiences. If you're not 
                    satisfied, we'll make it right.
                  </p>
                  <div className="flex items-center gap-4 text-sm">
                    <div className="flex items-center">
                      <div className="w-2 h-2 bg-green-500 rounded-full mr-2" />
                      <span>24/7 Support</span>
                    </div>
                    <div className="flex items-center">
                      <div className="w-2 h-2 bg-green-500 rounded-full mr-2" />
                      <span>Secure Payments</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>
      )}

      {/* CTA Section */}
      <section className="py-16 bg-gradient-to-br from-gray-900 to-gray-800 text-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold mb-4">
            Still Have Questions?
          </h2>
          <p className="text-gray-300 text-lg mb-8">
            Our friendly support team is available 24/7 to help you with anything you need.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/contact">
              <Button size="lg" className="bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700">
                <MessageSquare className="w-5 h-5 mr-2" />
                Contact Support
              </Button>
            </Link>
            <Button size="lg" variant="outline" className="border-white text-white hover:bg-white/10">
              <Phone className="w-5 h-5 mr-2" />
              Call Us Now
            </Button>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HelpCenterPage;
