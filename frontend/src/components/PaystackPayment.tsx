import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';
import api from '@/lib/api';

// Paystack SDK type declaration
declare global {
  interface Window {
    PaystackPop: {
      setup: (config: {
        key: string;
        email: string;
        amount: number;
        ref: string;
        callback: (response: { reference: string }) => void;
        onClose: () => void;
        metadata?: Record<string, unknown>;
      }) => {
        openIframe: () => void;
      };
    };
  }
}

interface PaystackPaymentProps {
  voucherProductId: string;
  nightsIncluded: number;
  email: string;
  amountKobo: number;
  onSuccess: (reference: string) => void;
  onCancel?: () => void;
  buttonText?: string;
  disabled?: boolean;
}

export function PaystackPayment({
  voucherProductId,
  nightsIncluded,
  email,
  amountKobo,
  onSuccess,
  onCancel,
  buttonText = 'Pay Now',
  disabled = false,
}: PaystackPaymentProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [paystackKey, setPaystackKey] = useState<string>('');
  const [scriptLoaded, setScriptLoaded] = useState(false);

  // Load Paystack script
  useEffect(() => {
    const existingScript = document.getElementById('paystack-script');
    if (existingScript) {
      setScriptLoaded(true);
      return;
    }

    const script = document.createElement('script');
    script.id = 'paystack-script';
    script.src = 'https://js.paystack.co/v1/inline.js';
    script.async = true;
    script.onload = () => setScriptLoaded(true);
    script.onerror = () => {
      toast.error('Failed to load payment system');
    };
    document.body.appendChild(script);

    return () => {
      // Don't remove script on unmount to avoid reloading
    };
  }, []);

  // Fetch Paystack public key
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const response = await api.get('/paystack/config');
        setPaystackKey(response.data.public_key);
      } catch (error) {
        console.error('Failed to fetch Paystack config:', error);
        toast.error('Failed to initialize payment system');
      }
    };

    if (scriptLoaded) {
      fetchConfig();
    }
  }, [scriptLoaded]);

  const initializePayment = async () => {
    if (!scriptLoaded || !window.PaystackPop) {
      toast.error('Payment system not loaded. Please try again.');
      return;
    }

    if (!paystackKey) {
      toast.error('Payment configuration not available');
      return;
    }

    setIsLoading(true);

    try {
      // Initialize payment on backend to get reference
      const callbackUrl = `${window.location.origin}/payment/callback`;
      const response = await api.post('/paystack/initialize', {
        voucher_product_id: voucherProductId,
        nights_included: nightsIncluded,
        email,
        callback_url: callbackUrl,
      });

      const { reference, success, message } = response.data;

      if (!success || !reference) {
        toast.error(message || 'Failed to initialize payment');
        setIsLoading(false);
        return;
      }

      // Open Paystack inline payment
      const handler = window.PaystackPop.setup({
        key: paystackKey,
        email,
        amount: amountKobo,
        ref: reference,
        callback: (response) => {
          // Payment completed
          onSuccess(response.reference);
          setIsLoading(false);
        },
        onClose: () => {
          // Payment window closed
          setIsLoading(false);
          onCancel?.();
        },
        metadata: {
          voucher_product_id: voucherProductId,
          nights_included: nightsIncluded,
          custom_fields: [
            {
              display_name: 'Product',
              variable_name: 'product_name',
              value: 'StayFlex Voucher',
            },
          ],
        },
      });

      handler.openIframe();
    } catch (error) {
      console.error('Payment initialization error:', error);
      toast.error('Failed to start payment. Please try again.');
      setIsLoading(false);
    }
  };

  return (
    <Button
      onClick={initializePayment}
      disabled={disabled || isLoading || !scriptLoaded || !paystackKey}
      className="w-full"
      size="lg"
    >
      {isLoading ? (
        <>
          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          Processing...
        </>
      ) : (
        buttonText
      )}
    </Button>
  );
}

export default PaystackPayment;
