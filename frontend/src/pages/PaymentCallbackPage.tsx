import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2, CheckCircle, XCircle } from 'lucide-react';
import { toast } from 'sonner';
import api from '@/lib/axios';

export function PaymentCallbackPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState<'verifying' | 'success' | 'failed'>('verifying');
  const [reference, setReference] = useState('');

  useEffect(() => {
    const trxref = searchParams.get('trxref');
    const ref = searchParams.get('reference');
    const paymentRef = trxref || ref;

    if (!paymentRef) {
      toast.error('Invalid payment reference');
      navigate('/packages');
      return;
    }

    setReference(paymentRef);
    verifyPayment(paymentRef);
  }, [searchParams]);

  const verifyPayment = async (paymentRef: string) => {
    try {
      const response = await api.get(`/paystack/verify/${paymentRef}`);
      
      if (response.data.success && response.data.status === 'success') {
        setStatus('success');
        toast.success('Payment successful! Your voucher has been activated.');
      } else {
        setStatus('failed');
        toast.error('Payment verification failed');
      }
    } catch (error) {
      console.error('Payment verification error:', error);
      setStatus('failed');
      toast.error('Failed to verify payment');
    }
  };

  if (status === 'verifying') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Card className="w-full max-w-md mx-4">
          <CardContent className="pt-8 pb-8 text-center">
            <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto mb-4" />
            <h2 className="text-xl font-semibold mb-2">Verifying Payment...</h2>
            <p className="text-gray-600">Please wait while we confirm your payment</p>
            {reference && (
              <p className="text-sm text-gray-500 mt-4 font-mono">Ref: {reference}</p>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }

  if (status === 'success') {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Card className="w-full max-w-md mx-4">
          <CardContent className="pt-8 pb-8 text-center">
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
              <p className="font-mono text-sm">{reference}</p>
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
    );
  }

  // Failed state
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <Card className="w-full max-w-md mx-4">
        <CardContent className="pt-8 pb-8 text-center">
          <div className="w-20 h-20 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <XCircle className="h-10 w-10 text-red-600" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Payment Failed
          </h1>
          <p className="text-gray-600 mb-6">
            We couldn&apos;t verify your payment. Please try again or contact support.
          </p>
          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <p className="text-sm text-gray-500 mb-1">Reference</p>
            <p className="font-mono text-sm">{reference}</p>
          </div>
          <div className="space-y-3">
            <Button 
              onClick={() => navigate('/packages')} 
              className="w-full"
            >
              Try Again
            </Button>
            <Button 
              variant="outline" 
              onClick={() => navigate('/contact')}
              className="w-full"
            >
              Contact Support
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default PaymentCallbackPage;
