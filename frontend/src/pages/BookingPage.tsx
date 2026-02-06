import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useVouchers } from '@/hooks/usePackages';
import { bookingsApi } from '@/lib/api';
import { useMutation, useQuery } from '@tanstack/react-query';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Calendar } from '@/components/ui/calendar';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { format } from 'date-fns';
import {
  Calendar as CalendarIcon,
  MapPin,
  Star,
  Bed,
  Users,
  ArrowLeft,
  Check,
  Loader2,
} from 'lucide-react';
import { toast } from 'sonner';

const BookingPage = () => {
  const { voucherId } = useParams<{ voucherId: string }>();
  const navigate = useNavigate();
  const [selectedDate, setSelectedDate] = useState<Date>();
  const [selectedProperty, setSelectedProperty] = useState<any>(null);
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);

  const { data: vouchers } = useVouchers();
  const voucher = vouchers?.find((v: any) => v.id === voucherId);

  // Fetch eligible properties
  const { data: eligibleData, isLoading: isLoadingProperties } = useQuery({
    queryKey: ['eligible-properties', voucherId, selectedDate],
    queryFn: async () => {
      if (!voucherId || !selectedDate) return null;
      const response = await bookingsApi.getEligibleProperties(
        voucherId,
        format(selectedDate, 'yyyy-MM-dd')
      );
      return response.data;
    },
    enabled: !!voucherId && !!selectedDate,
  });

  const bookMutation = useMutation({
    mutationFn: (data: {
      voucher_id: string;
      property_id: string;
      availability_id: string;
      check_in_date: string;
    }) => bookingsApi.create(data),
    onSuccess: () => {
      toast.success('Booking created successfully!');
      navigate('/my-vouchers');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Booking failed');
    },
  });

  if (!voucher) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-2">Voucher not found</h2>
          <Button onClick={() => navigate('/my-vouchers')}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to My Vouchers
          </Button>
        </div>
      </div>
    );
  }

  const handleBook = async () => {
    if (!selectedProperty || !selectedDate) return;

    await bookMutation.mutateAsync({
      voucher_id: voucherId!,
      property_id: selectedProperty.property.id,
      availability_id: selectedProperty.availability.id,
      check_in_date: format(selectedDate, 'yyyy-MM-dd'),
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <Button
          variant="ghost"
          className="mb-6"
          onClick={() => navigate('/my-vouchers')}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to My Vouchers
        </Button>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            <h1 className="text-3xl font-bold mb-2">Book Your Stay</h1>
            <p className="text-gray-600 mb-8">
              Select your check-in date and choose from available properties
            </p>

            {/* Date Selection */}
            <Card className="mb-8">
              <CardContent className="p-6">
                <h3 className="text-lg font-semibold mb-4">Select Check-in Date</h3>
                <Popover>
                  <PopoverTrigger asChild>
                    <Button
                      variant="outline"
                      className="w-full justify-start text-left font-normal"
                    >
                      <CalendarIcon className="mr-2 h-4 w-4" />
                      {selectedDate ? (
                        format(selectedDate, 'PPP')
                      ) : (
                        <span>Pick a date</span>
                      )}
                    </Button>
                  </PopoverTrigger>
                  <PopoverContent className="w-auto p-0" align="start">
                    <Calendar
                      mode="single"
                      selected={selectedDate}
                      onSelect={setSelectedDate}
                      disabled={(date) =>
                        date < new Date(voucher.valid_from) ||
                        date > new Date(voucher.valid_until) ||
                        date < new Date()
                      }
                      initialFocus
                    />
                  </PopoverContent>
                </Popover>
                <p className="text-sm text-gray-500 mt-2">
                  Voucher valid from{' '}
                  {format(new Date(voucher.valid_from), 'MMM d, yyyy')} to{' '}
                  {format(new Date(voucher.valid_until), 'MMM d, yyyy')}
                </p>
              </CardContent>
            </Card>

            {/* Properties List */}
            {selectedDate && (
              <div>
                <h3 className="text-lg font-semibold mb-4">
                  Available Properties ({eligibleData?.eligible_properties?.length || 0})
                </h3>

                {isLoadingProperties ? (
                  <div className="space-y-4">
                    {[1, 2, 3].map((i) => (
                      <Card key={i} className="animate-pulse">
                        <div className="h-32 bg-gray-200" />
                      </Card>
                    ))}
                  </div>
                ) : eligibleData?.eligible_properties?.length === 0 ? (
                  <Card>
                    <CardContent className="p-8 text-center">
                      <p className="text-gray-600">
                        No properties available for the selected date.
                      </p>
                      <p className="text-sm text-gray-500 mt-1">
                        Try selecting a different date.
                      </p>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="space-y-4">
                    {eligibleData?.eligible_properties?.map((item: any) => (
                      <Card
                        key={item.property.id}
                        className={`cursor-pointer transition-all ${
                          selectedProperty?.property.id === item.property.id
                            ? 'ring-2 ring-amber-500'
                            : 'hover:shadow-md'
                        }`}
                        onClick={() => setSelectedProperty(item)}
                      >
                        <CardContent className="p-6">
                          <div className="flex items-start gap-4">
                            <div className="w-24 h-24 bg-gray-200 rounded-lg flex-shrink-0">
                              {item.property.images?.[0] ? (
                                <img
                                  src={item.property.images[0]}
                                  alt={item.property.name}
                                  className="w-full h-full object-cover rounded-lg"
                                />
                              ) : (
                                <div className="w-full h-full flex items-center justify-center">
                                  <Bed className="w-8 h-8 text-gray-400" />
                                </div>
                              )}
                            </div>
                            <div className="flex-1">
                              <div className="flex items-start justify-between">
                                <div>
                                  <h4 className="font-semibold text-lg">
                                    {item.property.name}
                                  </h4>
                                  <div className="flex items-center text-sm text-gray-500 mt-1">
                                    <MapPin className="w-4 h-4 mr-1" />
                                    {item.property.city}, {item.property.state}
                                  </div>
                                </div>
                                <Badge variant="secondary">
                                  <Star className="w-3 h-3 mr-1 fill-amber-500 text-amber-500" />
                                  4.5
                                </Badge>
                              </div>
                              <div className="flex items-center gap-4 mt-3 text-sm">
                                <div className="flex items-center">
                                  <Bed className="w-4 h-4 mr-1 text-gray-400" />
                                  {item.property.property_type}
                                </div>
                                <div className="flex items-center">
                                  <Users className="w-4 h-4 mr-1 text-gray-400" />
                                  Up to {voucher.nights_included} guests
                                </div>
                              </div>
                              <div className="mt-3 pt-3 border-t flex items-center justify-between">
                                <div>
                                  <span className="text-sm text-gray-500">Price per night</span>
                                  <p className="font-semibold">
                                    ₦{(item.availability.accepted_voucher_price_kobo / 100).toLocaleString()}
                                  </p>
                                </div>
                                {item.savings_kobo > 0 && (
                                  <Badge className="bg-green-100 text-green-700">
                                    Save ₦{(item.savings_kobo / 100).toLocaleString()}
                                  </Badge>
                                )}
                              </div>
                            </div>
                          </div>
                          {selectedProperty?.property.id === item.property.id && (
                            <div className="mt-4 pt-4 border-t flex items-center justify-center text-amber-600">
                              <Check className="w-5 h-5 mr-2" />
                              Selected
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Booking Summary */}
          <div>
            <Card className="sticky top-24">
              <CardContent className="p-6">
                <h3 className="text-lg font-semibold mb-4">Booking Summary</h3>

                <div className="space-y-4 mb-6">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Voucher</span>
                    <span className="font-medium">{voucher.code}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Nights</span>
                    <span className="font-medium">{voucher.nights_included}</span>
                  </div>
                  {selectedDate && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Check-in</span>
                      <span className="font-medium">
                        {format(selectedDate, 'MMM d, yyyy')}
                      </span>
                    </div>
                  )}
                  {selectedProperty && (
                    <div className="flex justify-between">
                      <span className="text-gray-600">Property</span>
                      <span className="font-medium text-right max-w-[150px]">
                        {selectedProperty.property.name}
                      </span>
                    </div>
                  )}
                </div>

                <div className="border-t pt-4 mb-6">
                  <div className="flex justify-between items-center">
                    <span className="font-semibold">Total Value</span>
                    <span className="text-xl font-bold text-amber-600">
                      ₦{(voucher.original_value_kobo / 100).toLocaleString()}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500 mt-1">
                    Paid: ₦{(voucher.purchase_price_kobo / 100).toLocaleString()}
                  </p>
                </div>

                <Button
                  className="w-full bg-gradient-to-r from-amber-500 to-orange-600"
                  disabled={!selectedProperty || bookMutation.isPending}
                  onClick={() => setShowConfirmDialog(true)}
                >
                  {bookMutation.isPending ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Booking...
                    </>
                  ) : (
                    'Confirm Booking'
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* Confirmation Dialog */}
      <Dialog open={showConfirmDialog} onOpenChange={setShowConfirmDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirm Your Booking</DialogTitle>
            <DialogDescription>
              Please review your booking details before confirming.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="bg-gray-50 p-4 rounded-lg space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600">Property</span>
                <span className="font-medium">{selectedProperty?.property.name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Check-in</span>
                <span className="font-medium">
                  {selectedDate && format(selectedDate, 'MMM d, yyyy')}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Nights</span>
                <span className="font-medium">{voucher.nights_included}</span>
              </div>
            </div>
            <p className="text-sm text-gray-500">
              By confirming, you agree to the property's terms and conditions.
            </p>
          </div>
          <div className="flex gap-3">
            <Button
              variant="outline"
              className="flex-1"
              onClick={() => setShowConfirmDialog(false)}
            >
              Cancel
            </Button>
            <Button
              className="flex-1 bg-gradient-to-r from-amber-500 to-orange-600"
              onClick={handleBook}
              disabled={bookMutation.isPending}
            >
              {bookMutation.isPending ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Booking...
                </>
              ) : (
                'Confirm Booking'
              )}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default BookingPage;
