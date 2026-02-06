import { Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { useVouchers } from '@/hooks/usePackages';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Gift,
  Calendar,
  MapPin,
  ArrowRight,
  Clock,
  CheckCircle,
  AlertCircle,
} from 'lucide-react';

const DashboardPage = () => {
  const { user } = useAuth();
  const { data: vouchers, isLoading } = useVouchers();

  // Calculate stats
  const activeVouchers = vouchers?.filter((v: any) => v.status === 'active').length || 0;
  const totalVouchers = vouchers?.length || 0;
  const redeemedVouchers = vouchers?.filter((v: any) => v.status === 'redeemed').length || 0;

  const stats = [
    { label: 'Active Vouchers', value: activeVouchers, icon: Gift, color: 'text-amber-600', bgColor: 'bg-amber-100' },
    { label: 'Total Purchases', value: totalVouchers, icon: CheckCircle, color: 'text-green-600', bgColor: 'bg-green-100' },
    { label: 'Completed Stays', value: redeemedVouchers, icon: Calendar, color: 'text-blue-600', bgColor: 'bg-blue-100' },
  ];

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
    return days > 0 ? `${days} days left` : 'Expired';
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Welcome Section */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">
            Welcome back, {user?.full_name || user?.business_name}!
          </h1>
          <p className="text-gray-600">
            Here's what's happening with your vouchers
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {stats.map((stat) => (
            <Card key={stat.label}>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <div className={`w-12 h-12 ${stat.bgColor} rounded-xl flex items-center justify-center mr-4`}>
                    <stat.icon className={`w-6 h-6 ${stat.color}`} />
                  </div>
                  <div>
                    <p className="text-gray-600 text-sm">{stat.label}</p>
                    <p className="text-2xl font-bold">{stat.value}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Recent Vouchers */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Your Vouchers</CardTitle>
            <Link to="/my-vouchers">
              <Button variant="ghost" size="sm">
                View All
                <ArrowRight className="w-4 h-4 ml-1" />
              </Button>
            </Link>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-20 bg-gray-100 rounded-lg animate-pulse" />
                ))}
              </div>
            ) : vouchers?.length === 0 ? (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Gift className="w-8 h-8 text-gray-400" />
                </div>
                <h3 className="text-lg font-semibold mb-2">No vouchers yet</h3>
                <p className="text-gray-600 mb-4">
                  Start by browsing our experience packages
                </p>
                <Link to="/packages">
                  <Button className="bg-gradient-to-r from-amber-500 to-orange-600">
                    Browse Packages
                  </Button>
                </Link>
              </div>
            ) : (
              <div className="space-y-4">
                {vouchers?.slice(0, 5).map((voucher: any) => (
                  <div
                    key={voucher.id}
                    className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <div className="flex items-center">
                      <div className="w-12 h-12 bg-amber-100 rounded-lg flex items-center justify-center mr-4">
                        <Gift className="w-6 h-6 text-amber-600" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <p className="font-semibold">{voucher.code}</p>
                          {getStatusBadge(voucher.status)}
                        </div>
                        <div className="flex items-center text-sm text-gray-500 mt-1">
                          <MapPin className="w-3 h-3 mr-1" />
                          {voucher.city}
                          <span className="mx-2">•</span>
                          <Clock className="w-3 h-3 mr-1" />
                          {getDaysUntilExpiry(voucher.valid_until)}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-amber-600">
                        ₦{(voucher.purchase_price_kobo / 100).toLocaleString()}
                      </p>
                      <p className="text-sm text-gray-500">
                        {voucher.nights_included} nights
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-start">
                <div className="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center mr-4">
                  <Gift className="w-6 h-6 text-amber-600" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold mb-1">Browse Packages</h3>
                  <p className="text-gray-600 text-sm mb-4">
                    Discover new experience packages and gift ideas
                  </p>
                  <Link to="/packages">
                    <Button variant="outline" size="sm">
                      Explore
                      <ArrowRight className="w-4 h-4 ml-1" />
                    </Button>
                  </Link>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-start">
                <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mr-4">
                  <AlertCircle className="w-6 h-6 text-blue-600" />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold mb-1">Need Help?</h3>
                  <p className="text-gray-600 text-sm mb-4">
                    Contact our support team for assistance
                  </p>
                  <Button variant="outline" size="sm">
                    Contact Support
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
