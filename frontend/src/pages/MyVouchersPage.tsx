import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useVouchers } from '@/hooks/usePackages';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Gift,
  MapPin,
  Calendar,
  Clock,
  ArrowRight,
  Search,
  QrCode,
} from 'lucide-react';
import { Input } from '@/components/ui/input';

const MyVouchersPage = () => {
  const { data: vouchers, isLoading } = useVouchers();
  const [searchQuery, setSearchQuery] = useState('');

  // Filter vouchers
  const filteredVouchers = vouchers?.filter((voucher: any) => {
    return (
      searchQuery === '' ||
      voucher.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
      voucher.city.toLowerCase().includes(searchQuery.toLowerCase())
    );
  });

  // Group vouchers by status
  const groupedVouchers = {
    active: filteredVouchers?.filter((v: any) => v.status === 'active') || [],
    reserved: filteredVouchers?.filter((v: any) => v.status === 'reserved') || [],
    redeemed: filteredVouchers?.filter((v: any) => v.status === 'redeemed') || [],
    expired: filteredVouchers?.filter((v: any) => v.status === 'expired') || [],
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return <Badge className="bg-green-500">Active</Badge>;
      case 'reserved':
        return <Badge className="bg-blue-500">Reserved</Badge>;
      case 'redeemed':
        return <Badge className="bg-gray-500">Redeemed</Badge>;
      case 'expired':
        return <Badge variant="destructive">Expired</Badge>;
      default:
        return <Badge variant="secondary">{status}</Badge>;
    }
  };

  const getDaysUntilExpiry = (validUntil: string) => {
    const days = Math.ceil((new Date(validUntil).getTime() - Date.now()) / (1000 * 60 * 60 * 24));
    if (days < 0) return 'Expired';
    if (days === 0) return 'Expires today';
    if (days === 1) return '1 day left';
    return `${days} days left`;
  };

  const VoucherCard = ({ voucher }: { voucher: any }) => (
    <Card className="overflow-hidden hover:shadow-lg transition-shadow">
      <CardContent className="p-0">
        <div className="p-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center">
              <div className="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center mr-4">
                <Gift className="w-6 h-6 text-amber-600" />
              </div>
              <div>
                <p className="font-semibold text-lg">{voucher.code}</p>
                <div className="flex items-center text-sm text-gray-500 mt-1">
                  <MapPin className="w-3 h-3 mr-1" />
                  {voucher.city}
                </div>
              </div>
            </div>
            {getStatusBadge(voucher.status)}
          </div>

          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="bg-gray-50 p-3 rounded-lg">
              <p className="text-sm text-gray-500">Valid Until</p>
              <div className="flex items-center">
                <Calendar className="w-4 h-4 mr-1 text-amber-600" />
                <span className="font-medium">
                  {new Date(voucher.valid_until).toLocaleDateString()}
                </span>
              </div>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg">
              <p className="text-sm text-gray-500">Time Remaining</p>
              <div className="flex items-center">
                <Clock className="w-4 h-4 mr-1 text-amber-600" />
                <span className="font-medium">{getDaysUntilExpiry(voucher.valid_until)}</span>
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between pt-4 border-t">
            <div>
              <p className="text-sm text-gray-500">Purchase Price</p>
              <p className="text-xl font-bold text-amber-600">
                ₦{(voucher.purchase_price_kobo / 100).toLocaleString()}
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">Nights</p>
              <p className="font-medium">{voucher.nights_included}</p>
            </div>
          </div>
        </div>

        {voucher.status === 'active' && (
          <div className="px-6 pb-6">
            <Link to={`/book/${voucher.id}`}>
              <Button className="w-full bg-gradient-to-r from-amber-500 to-orange-600">
                Book Now
                <ArrowRight className="w-4 h-4 ml-2" />
              </Button>
            </Link>
          </div>
        )}

        {voucher.status === 'reserved' && (
          <div className="px-6 pb-6">
            <Button variant="outline" className="w-full" disabled>
              <QrCode className="w-4 h-4 mr-2" />
              Show at Check-in
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold mb-2">My Vouchers</h1>
            <p className="text-gray-600">
              Manage your experience vouchers and bookings
            </p>
          </div>
          <Link to="/packages" className="mt-4 md:mt-0">
            <Button className="bg-gradient-to-r from-amber-500 to-orange-600">
              <Gift className="w-4 h-4 mr-2" />
              Buy New Voucher
            </Button>
          </Link>
        </div>

        {/* Search */}
        <div className="relative mb-8">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
          <Input
            placeholder="Search vouchers by code or city..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Vouchers Tabs */}
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((i) => (
              <Card key={i} className="animate-pulse">
                <div className="h-48 bg-gray-200" />
              </Card>
            ))}
          </div>
        ) : filteredVouchers?.length === 0 ? (
          <div className="text-center py-16">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Gift className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-xl font-semibold mb-2">No vouchers found</h3>
            <p className="text-gray-600 mb-4">
              {searchQuery
                ? 'Try adjusting your search'
                : 'Start by purchasing your first experience package'}
            </p>
            {!searchQuery && (
              <Link to="/packages">
                <Button className="bg-gradient-to-r from-amber-500 to-orange-600">
                  Browse Packages
                </Button>
              </Link>
            )}
          </div>
        ) : (
          <Tabs defaultValue="active">
            <TabsList className="mb-6">
              <TabsTrigger value="active">
                Active ({groupedVouchers.active.length})
              </TabsTrigger>
              <TabsTrigger value="reserved">
                Reserved ({groupedVouchers.reserved.length})
              </TabsTrigger>
              <TabsTrigger value="redeemed">
                Redeemed ({groupedVouchers.redeemed.length})
              </TabsTrigger>
              <TabsTrigger value="expired">
                Expired ({groupedVouchers.expired.length})
              </TabsTrigger>
            </TabsList>

            {Object.entries(groupedVouchers).map(([status, vouchers]) => (
              <TabsContent key={status} value={status}>
                {vouchers.length === 0 ? (
                  <div className="text-center py-12">
                    <p className="text-gray-500">No {status} vouchers</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {vouchers.map((voucher: any) => (
                      <VoucherCard key={voucher.id} voucher={voucher} />
                    ))}
                  </div>
                )}
              </TabsContent>
            ))}
          </Tabs>
        )}
      </div>
    </div>
  );
};

export default MyVouchersPage;
