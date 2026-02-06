import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { authApi } from '@/lib/api';
import { toast } from 'sonner';

export const useLogin = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      authApi.login(email, password),
    onSuccess: (response) => {
      const { access_token, user_type } = response.data;
      localStorage.setItem('token', access_token);
      localStorage.setItem('user_type', user_type);
      queryClient.invalidateQueries({ queryKey: ['me'] });
      toast.success('Login successful!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Login failed');
    },
  });
};

export const useRegister = () => {
  return useMutation({
    mutationFn: (data: {
      email: string;
      password: string;
      full_name: string;
      phone: string;
    }) => authApi.register(data),
    onSuccess: () => {
      toast.success('Account created successfully! Please log in.');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Registration failed');
    },
  });
};

export const useMe = () => {
  return useQuery({
    queryKey: ['me'],
    queryFn: async () => {
      const response = await authApi.me();
      return response.data;
    },
    enabled: !!localStorage.getItem('token'),
    retry: false,
  });
};
