import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { packagesApi, vouchersApi } from '@/lib/api';
import { toast } from 'sonner';

export const usePackages = (params?: { city?: string; featured_only?: boolean }) => {
  return useQuery({
    queryKey: ['packages', params],
    queryFn: async () => {
      const response = await packagesApi.list(params);
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const usePackage = (slug: string) => {
  return useQuery({
    queryKey: ['package', slug],
    queryFn: async () => {
      const response = await packagesApi.getBySlug(slug);
      return response.data;
    },
    enabled: !!slug,
    staleTime: 5 * 60 * 1000,
  });
};

export const useVouchers = () => {
  return useQuery({
    queryKey: ['vouchers'],
    queryFn: async () => {
      const response = await vouchersApi.list();
      return response.data;
    },
  });
};

export const usePurchaseVoucher = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: {
      experience_package_id: string;
      nights_included: number;
      payment_method: string;
      payment_gateway: string;
    }) => vouchersApi.purchase(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['vouchers'] });
      toast.success('Voucher purchased successfully!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Purchase failed');
    },
  });
};
