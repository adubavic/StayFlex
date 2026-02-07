import { useState, useEffect } from 'react';
import { useParams, useNavigate, useSearchParams } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { Badge } from '@/components/ui/badge';
import { PaystackPayment } from '@/components/PaystackPayment';
import { useAuth } from '@/hooks/useAuth';
import { toast } from 'sonner';
import { Loader2, CheckCircle, MapPin, Calendar, Moon, Tag, Shield } from 'lucide-react';
import api from '@/lib/axios';

interface VoucherProduct {
  id: string;
  name: string;
  description: string;
  city: string;
  state: string;
  max_price_per_night_kobo: number;
  validity_days: number;
  discount_percentage: number;
}

export function CheckoutPage() {
  const { productId } = useParams<{ productId: string }>();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { user, isAuthenticated } = useAuth();
  
  const [product, setProduct] = useState<VoucherProduct | null>(null);
  const [nights, setNights] = useState(() => {
    const nightsParam = searchParams.get('nights');
    return nightsParam ? parseInt(nightsParam, 10) : 2;
  });
  const [email, setEmail] = useState(user?.email || '');
  const [isLoading, setIsLoading] = useState(true);
  const [paymentSuccess, setPaymentSuccess] = useState(false);
  const [paymentReference, setPaymentReference] = useState('');

  useEffect(() => {
    if (!isAuthenticated) {
      toast.error('Please login to continue');
      navigate('/login', { state: { from: `/checkout/${productId}` } });
      return;
    }

    fetchProduct();
  }, [productId, isAuthenticated]);

  useEffect(() => {
    if (user?.email) {
      setEmail(user.email);
    }
  }, [user]);

  const fetchProduct = async () => {
    try {
      const response = await api.get(`/admin/voucher-products/${productId}`);
      setProduct(response.data);
    } catch (error) {
      toast.error('Failed to load product details');
      navigate('/packages');
    } finally {
      setIsLoading(false);
    }
  };

  const handlePaymentSuccess = async (reference: string) => {
    setPaymentReference(reference);
    
    // Verify payment
    try {
      const response = await api.get(`/paystack/verify/${reference}`);
      if (response.data.success && response.data.status === 'success') {
        setPaymentSuccess(true);
        toast.success('Payment successful! Your voucher has been activated.');
      } else {
        toast.error('Payment verification failed. Please contact support.');
      }
    } catch (error) {
      toast.error('Failed to verify payment. Please contact support.');
    }
  };

  const handlePaymentCancel = () => {
    toast.info('Payment cancelled. You can try again anytime.');
  };

  const formatCurrency = (kobo: number) => {
    return new Intl.NumberFormat('en-NG', {
      style: 'currency',
      currency: 'NGN',
    }).format(kobo / 100);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  if (paymentSuccess) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-md mx-auto px-4">
          <Card className="text-center">
            <CardContent className="pt-8 pb-8">
              <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <CheckCircle className="h-10 w-10 text-green-600" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                Payment Successful!
              </h1>
              <p className="text-gray-600 mb-6">
                Your voucher has been activated and is ready to use.
              </p>
              <div className="bg-gray-50 rounded-lg p-4 mb-6">
                <p className="text-sm text-gray-500 mb-1">Payment Reference</p>
                <p className="font-mono text-sm">{paymentReference}</p>
              </div>
              <div className="space-y-3">
                <Button 
                  onClick={() => navigate('/dashboard')} 
                  className="w-full"
                >
                  View My Vouchers
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => navigate('/packages')}
                  className="w-full"
                >
                  Browse More Packages
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-500">Product not found</p>
      </div>
    );
  }

  const originalValue = product.max_price_per_night_kobo * nights;
  const purchasePrice = Math.round(originalValue * (100 - product.discount_percentage) / 100);
  const savings = originalValue - purchasePrice;

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-6xl mx-auto px-4">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Checkout</h1>
          <p className="text-gray-600 mt-1">Complete your purchase securely</p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left Column - Order Summary */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle>Order Summary</CardTitle>
                <CardDescription>Review your purchase details</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Product Info */}
                <div className="bg-primary/5 rounded-lg p-4">
                  <h3 className="font-semibold text-lg mb-2">{product.name}</h3>
                  <p className="text-gray-600 text-sm mb-4">{product.description}</p>
                  <div className="flex flex-wrap gap-2">
                    <Badge variant="secondary" className="flex items-center gap-1">
                      <MapPin className="h-3 w-3" />
                      {product.city}, {product.state}
                    </Badge>
                    <Badge variant="secondary" className="flex items-center gap-1">
                      <Calendar className="h-3 w-3" />
                      Valid for {product.validity_days} days
                    </Badge>
                  </div>
                </div>

                {/* Nights Selector */}
                <div>
                  <Label htmlFor="nights" className="flex items-center gap-2 mb-2">
                    <Moon className="h-4 w-4" />
                    Number of Nights
                  </Label>
                  <div className="flex items-center gap-3">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setNights(Math.max(1, nights - 1))}
                      disabled={nights <= 1}
                    >
                      -
                    </Button>
                    <span className="font-semibold text-lg w-8 text-center">{nights}</span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setNights(Math.min(14, nights + 1))}
                      disabled={nights >= 14}
                    >
                      +
                    </Button>
                  </div>
                </div>

                <Separator />

                {/* Pricing Breakdown */}
                <div className="space-y-3">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Original Value ({nights} nights)</span>
                    <span className="line-through text-gray-400">
                      {formatCurrency(originalValue)}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600 flex items-center gap-1">
                      <Tag className="h-3 w-3" />
                      Discount ({product.discount_percentage}%)
                    </span>
                    <span className="text-green-600">-{formatCurrency(savings)}</span>
                  </div>
                  <Separator />
                  <div className="flex justify-between items-center">
                    <span className="font-semibold">Total to Pay</span>
                    <span className="text-2xl font-bold text-primary">
                      {formatCurrency(purchasePrice)}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Security Note */}
            <div className="mt-4 flex items-center gap-2 text-sm text-gray-500">
              <Shield className="h-4 w-4" />
              <span>Secure payment powered by Paystack</span>
            </div>
          </div>

          {/* Right Column - Payment */}
          <div>
            <Card>
              <CardHeader>
                <CardTitle>Payment Details</CardTitle>
                <CardDescription>Enter your payment information</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Email Input */}
                <div>
                  <Label htmlFor="email">Email Address</Label>
                  <Input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="your@email.com"
                    className="mt-1"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Payment receipt will be sent to this email
                  </p>
                </div>

                <Separator />

                {/* Paystack Payment */}
                <div>
                  <PaystackPayment
                    voucherProductId={product.id}
                    nightsIncluded={nights}
                    email={email}
                    amountKobo={purchasePrice}
                    onSuccess={handlePaymentSuccess}
                    onCancel={handlePaymentCancel}
                    buttonText={`Pay ${formatCurrency(purchasePrice)}`}
                    disabled={!email || !email.includes('@')}
                  />
                </div>

                {/* Alternative: Pay on Delivery/Transfer Note */}
                <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                  <p className="text-sm text-amber-800">
                    <strong>Note:</strong> This is a secure payment processed by Paystack. 
                    Your card details are never stored on our servers.
                  </p>
                </div>
              </CardContent>
              <CardFooter className="flex justify-between">
                <Button variant="outline" onClick={() => navigate('/packages')}>
                  Back to Packages
                </Button>
              </CardFooter>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CheckoutPage;
