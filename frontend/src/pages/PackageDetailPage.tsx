import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { usePackage, usePurchaseVoucher } from '@/hooks/usePackages';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Slider } from '@/components/ui/slider';
import {
  MapPin,
  Star,
  Calendar,
  Users,
  Coffee,
  Utensils,
  Sparkles,
  Mountain,
  Check,
  ArrowLeft,
  Gift,
  Clock,
  Shield,
} from 'lucide-react';
import { toast } from 'sonner';

const PackageDetailPage = () => {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  const { data: pkg, isLoading } = usePackage(slug || '');
  const purchaseMutation = usePurchaseVoucher();
  
  const [nights, setNights] = useState(2);
  const [showPurchaseDialog, setShowPurchaseDialog] = useState(false);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-600" />
      </div>
    );
  }

  if (!pkg) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-2">Package not found</h2>
          <p className="text-gray-600 mb-4">
            The package you're looking for doesn't exist.
          </p>
          <Button onClick={() => navigate('/packages')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Packages
          </Button>
        </div>
      </div>
    );
  }

  const totalPrice = pkg.base_price_kobo * nights;
  const totalValue = pkg.original_value_kobo * nights;
  const savings = totalValue - totalPrice;

  const handlePurchase = async () => {
    if (!isAuthenticated) {
      toast.error('Please log in to purchase');
      navigate('/login');
      return;
    }

    try {
      await purchaseMutation.mutateAsync({
        experience_package_id: pkg.id,
        nights_included: nights,
        payment_method: 'card',
        payment_gateway: 'paystack',
      });
      setShowPurchaseDialog(false);
      navigate('/my-vouchers');
    } catch (error) {
      // Error handled by mutation
    }
  };

  const features = [
    { icon: Calendar, label: `${nights} nights stay` },
    { icon: Users, label: `Up to ${pkg.max_guests} guests` },
    { icon: Clock, label: `Valid for ${pkg.validity_days} days` },
    ...(pkg.includes_breakfast ? [{ icon: Coffee, label: 'Breakfast included' }] : []),
    ...(pkg.includes_dinner ? [{ icon: Utensils, label: 'Dinner included' }] : []),
    ...(pkg.includes_spa ? [{ icon: Sparkles, label: 'Spa access' }] : []),
    ...(pkg.includes_activity ? [{ icon: Mountain, label: 'Activity included' }] : []),
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Image */}
      <div className="relative h-[50vh]">
        <img
          src={pkg.image_url || '/images/hero-hotel.jpg'}
          alt={pkg.name}
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 p-8">
          <div className="max-w-7xl mx-auto">
            <Button
              variant="ghost"
              className="text-white mb-4 hover:bg-white/20"
              onClick={() => navigate('/packages')}
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Packages
            </Button>
            <div className="flex items-center gap-2 mb-2">
              <Badge className="bg-amber-500">
                <Star className="w-3 h-3 mr-1 fill-white" />
                {pkg.rating} ({pkg.review_count} reviews)
              </Badge>
              <Badge variant="secondary" className="bg-white/90">
                <MapPin className="w-3 h-3 mr-1" />
                {pkg.city}, {pkg.state}
              </Badge>
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-2">
              {pkg.name}
            </h1>
            <p className="text-xl text-white/90">{pkg.tagline}</p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            <Tabs defaultValue="overview" className="w-full">
              <TabsList className="w-full justify-start">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="includes">What&apos;s Included</TabsTrigger>
                <TabsTrigger value="properties">Properties</TabsTrigger>
                <TabsTrigger value="terms">Terms</TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="mt-6">
                <Card>
                  <CardContent className="p-6">
                    <h3 className="text-xl font-semibold mb-4">About This Package</h3>
                    <p className="text-gray-600 leading-relaxed whitespace-pre-line">
                      {pkg.description}
                    </p>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="includes" className="mt-6">
                <Card>
                  <CardContent className="p-6">
                    <h3 className="text-xl font-semibold mb-4">What&apos;s Included</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {features.map((feature, index) => (
                        <div key={index} className="flex items-center">
                          <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center mr-3">
                            <feature.icon className="w-5 h-5 text-amber-600" />
                          </div>
                          <span>{feature.label}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="properties" className="mt-6">
                <Card>
                  <CardContent className="p-6">
                    <h3 className="text-xl font-semibold mb-4">Partner Properties</h3>
                    <p className="text-gray-600">
                      This package is valid at {pkg.property_types.length} types of properties:
                    </p>
                    <div className="flex flex-wrap gap-2 mt-4">
                      {pkg.property_types.map((type: string) => (
                        <Badge key={type} variant="secondary">
                          {type.charAt(0).toUpperCase() + type.slice(1)}
                        </Badge>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="terms" className="mt-6">
                <Card>
                  <CardContent className="p-6">
                    <h3 className="text-xl font-semibold mb-4">Terms & Conditions</h3>
                    <ul className="space-y-3 text-gray-600">
                      <li className="flex items-start">
                        <Check className="w-5 h-5 text-green-500 mr-2 mt-0.5" />
                        Voucher is valid for {pkg.validity_days} days from purchase
                      </li>
                      <li className="flex items-start">
                        <Check className="w-5 h-5 text-green-500 mr-2 mt-0.5" />
                        Free cancellation up to 48 hours before check-in
                      </li>
                      <li className="flex items-start">
                        <Check className="w-5 h-5 text-green-500 mr-2 mt-0.5" />
                        Subject to availability at partner properties
                      </li>
                      <li className="flex items-start">
                        <Check className="w-5 h-5 text-green-500 mr-2 mt-0.5" />
                        Blackout dates may apply during peak seasons
                      </li>
                    </ul>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>

          {/* Purchase Card */}
          <div>
            <Card className="sticky top-24">
              <CardContent className="p-6">
                <div className="mb-6">
                  <label className="text-sm font-medium text-gray-700 mb-2 block">
                    Number of Nights
                  </label>
                  <Slider
                    value={[nights]}
                    onValueChange={(value) => setNights(value[0])}
                    min={1}
                    max={14}
                    step={1}
                    className="mb-2"
                  />
                  <div className="flex justify-between text-sm text-gray-500">
                    <span>1 night</span>
                    <span className="font-semibold text-amber-600">{nights} nights</span>
                    <span>14 nights</span>
                  </div>
                </div>

                <div className="space-y-3 mb-6">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Original value</span>
                    <span className="line-through">
                      ₦{(totalValue / 100).toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Your price</span>
                    <span className="font-semibold text-amber-600">
                      ₦{(totalPrice / 100).toLocaleString()}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm text-green-600">
                    <span>You save</span>
                    <span>₦{(savings / 100).toLocaleString()}</span>
                  </div>
                </div>

                <div className="border-t pt-4 mb-6">
                  <div className="flex items-center justify-between mb-4">
                    <span className="text-lg font-semibold">Total</span>
                    <span className="text-2xl font-bold text-amber-600">
                      ₦{(totalPrice / 100).toLocaleString()}
                    </span>
                  </div>
                </div>

                <Button
                  className="w-full bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700"
                  size="lg"
                  onClick={() => setShowPurchaseDialog(true)}
                  disabled={purchaseMutation.isPending}
                >
                  <Gift className="w-5 h-5 mr-2" />
                  {purchaseMutation.isPending ? 'Processing...' : 'Purchase Now'}
                </Button>

                <div className="mt-4 flex items-center justify-center text-sm text-gray-500">
                  <Shield className="w-4 h-4 mr-1" />
                  Secure payment
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Purchase Dialog */}
      <Dialog open={showPurchaseDialog} onOpenChange={setShowPurchaseDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Confirm Purchase</DialogTitle>
            <DialogDescription>
              You&apos;re about to purchase the following experience package.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-semibold">{pkg.name}</h4>
              <p className="text-sm text-gray-600">{nights} nights in {pkg.city}</p>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Subtotal</span>
                <span>₦{(totalPrice / 100).toLocaleString()}</span>
              </div>
              <div className="flex justify-between font-semibold text-lg border-t pt-2">
                <span>Total</span>
                <span className="text-amber-600">
                  ₦{(totalPrice / 100).toLocaleString()}
                </span>
              </div>
            </div>
          </div>
          <div className="flex gap-3">
            <Button
              variant="outline"
              className="flex-1"
              onClick={() => setShowPurchaseDialog(false)}
            >
              Cancel
            </Button>
            <Button
              className="flex-1 bg-gradient-to-r from-amber-500 to-orange-600"
              onClick={handlePurchase}
              disabled={purchaseMutation.isPending}
            >
              {purchaseMutation.isPending ? 'Processing...' : 'Confirm Purchase'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default PackageDetailPage;
