import { useState } from 'react';
import { Link } from 'react-router-dom';
import { usePackages } from '@/hooks/usePackages';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { MapPin, Star, Search, SlidersHorizontal } from 'lucide-react';

const PackagesPage = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCity, setSelectedCity] = useState<string>('all');
  const { data: packages, isLoading } = usePackages();

  // Extract unique cities from packages
  const cities: string[] = packages
    ? ['all', ...(Array.from(new Set(packages.map((p: any) => String(p.city)))) as string[])]
    : ['all'];

  // Filter packages
  const filteredPackages = packages?.filter((pkg: any) => {
    const matchesSearch =
      searchQuery === '' ||
      pkg.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      pkg.city.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesCity = selectedCity === 'all' || pkg.city === selectedCity;

    return matchesSearch && matchesCity;
  });

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <h1 className="text-3xl md:text-4xl font-bold mb-4">
            Experience Packages
          </h1>
          <p className="text-gray-600">
            Browse our collection of curated hotel experience packages
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white border-b sticky top-16 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <Input
                placeholder="Search packages or cities..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
            <div className="flex gap-4">
              <Select value={selectedCity} onValueChange={setSelectedCity}>
                <SelectTrigger className="w-[180px]">
                  <MapPin className="w-4 h-4 mr-2" />
                  <SelectValue placeholder="Select city" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Cities</SelectItem>
                  {cities
                    .filter((c) => c !== 'all')
                    .map((city) => (
                      <SelectItem key={city} value={city}>
                        {city}
                      </SelectItem>
                    ))}
                </SelectContent>
              </Select>
              <Button variant="outline" className="hidden md:flex">
                <SlidersHorizontal className="w-4 h-4 mr-2" />
                Filters
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Packages Grid */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
              <Card key={i} className="animate-pulse">
                <div className="h-56 bg-gray-200" />
                <CardContent className="p-5">
                  <div className="h-5 bg-gray-200 rounded mb-2" />
                  <div className="h-4 bg-gray-200 rounded w-2/3" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : filteredPackages?.length === 0 ? (
          <div className="text-center py-16">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Search className="w-8 h-8 text-gray-400" />
            </div>
            <h3 className="text-xl font-semibold mb-2">No packages found</h3>
            <p className="text-gray-600">
              Try adjusting your search or filters to find what you're looking for.
            </p>
          </div>
        ) : (
          <>
            <p className="text-gray-600 mb-6">
              Showing {filteredPackages?.length} package
              {filteredPackages?.length !== 1 ? 's' : ''}
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {filteredPackages?.map((pkg: any) => (
                <Link key={pkg.id} to={`/packages/${pkg.slug}`}>
                  <Card className="overflow-hidden group cursor-pointer hover:shadow-xl transition-all duration-300 h-full">
                    <div className="relative h-56 overflow-hidden">
                      <img
                        src={pkg.image_url || '/images/hero-hotel.jpg'}
                        alt={pkg.name}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                      />
                      <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
                      <div className="absolute bottom-4 left-4 right-4">
                        <div className="flex items-center justify-between">
                          <Badge className="bg-white/90 text-gray-900">
                            <Star className="w-3 h-3 mr-1 text-amber-500 fill-amber-500" />
                            {pkg.rating}
                          </Badge>
                          {pkg.discount_percentage > 0 && (
                            <Badge className="bg-red-500 text-white">
                              -{pkg.discount_percentage}%
                            </Badge>
                          )}
                        </div>
                      </div>
                    </div>
                    <CardContent className="p-5">
                      <div className="flex items-center text-sm text-gray-500 mb-2">
                        <MapPin className="w-4 h-4 mr-1" />
                        {pkg.city}, {pkg.state}
                      </div>
                      <h3 className="text-lg font-semibold mb-2 line-clamp-1">
                        {pkg.name}
                      </h3>
                      <p className="text-gray-600 text-sm mb-4 line-clamp-2">
                        {pkg.short_description}
                      </p>
                      <div className="flex items-center justify-between pt-4 border-t">
                        <div>
                          <span className="text-xl font-bold text-amber-600">
                            ₦{(pkg.base_price_kobo / 100).toLocaleString()}
                          </span>
                          <span className="text-gray-400 text-sm line-through ml-2">
                            ₦{(pkg.original_value_kobo / 100).toLocaleString()}
                          </span>
                        </div>
                        <span className="text-sm text-gray-500">
                          {pkg.nights_included} nights
                        </span>
                      </div>
                      <div className="flex gap-2 mt-3">
                        {pkg.includes_breakfast && (
                          <Badge variant="secondary" className="text-xs">
                            Breakfast
                          </Badge>
                        )}
                        {pkg.includes_spa && (
                          <Badge variant="secondary" className="text-xs">
                            Spa
                          </Badge>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                </Link>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default PackagesPage;
