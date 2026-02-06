import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useRegister } from '@/hooks/useAuth';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Gift, Eye, EyeOff, Check, X } from 'lucide-react';

const RegisterPage = () => {
  const navigate = useNavigate();
  const registerMutation = useRegister();
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone: '',
    password: '',
  });

  // Password validation
  const passwordChecks = {
    length: formData.password.length >= 8,
    uppercase: /[A-Z]/.test(formData.password),
    lowercase: /[a-z]/.test(formData.password),
    number: /\d/.test(formData.password),
    special: /[!@#$%^&*(),.?":{}|<>]/.test(formData.password),
  };

  const isPasswordValid = Object.values(passwordChecks).every(Boolean);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isPasswordValid) return;

    try {
      await registerMutation.mutateAsync(formData);
      navigate('/login');
    } catch (error) {
      // Error handled by mutation
    }
  };

  return (
    <Card className="w-full">
      <CardHeader className="text-center">
        <div className="w-12 h-12 bg-gradient-to-br from-amber-500 to-orange-600 rounded-xl flex items-center justify-center mx-auto mb-4">
          <Gift className="w-6 h-6 text-white" />
        </div>
        <CardTitle className="text-2xl">Create an account</CardTitle>
        <CardDescription>
          Start gifting unforgettable experiences today
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="full_name">Full Name</Label>
            <Input
              id="full_name"
              placeholder="John Doe"
              value={formData.full_name}
              onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="you@example.com"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="phone">Phone Number</Label>
            <Input
              id="phone"
              type="tel"
              placeholder="+1234567890"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              required
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <div className="relative">
              <Input
                id="password"
                type={showPassword ? 'text' : 'password'}
                placeholder="Create a password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                required
              />
              <button
                type="button"
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
            {/* Password requirements */}
            <div className="space-y-1 mt-2">
              {Object.entries(passwordChecks).map(([key, valid]) => (
                <div key={key} className={`flex items-center text-xs ${valid ? 'text-green-600' : 'text-gray-500'}`}>
                  {valid ? <Check className="w-3 h-3 mr-1" /> : <X className="w-3 h-3 mr-1" />}
                  {key === 'length' && 'At least 8 characters'}
                  {key === 'uppercase' && 'One uppercase letter'}
                  {key === 'lowercase' && 'One lowercase letter'}
                  {key === 'number' && 'One number'}
                  {key === 'special' && 'One special character'}
                </div>
              ))}
            </div>
          </div>
          <Button
            type="submit"
            className="w-full bg-gradient-to-r from-amber-500 to-orange-600 hover:from-amber-600 hover:to-orange-700"
            disabled={registerMutation.isPending || !isPasswordValid}
          >
            {registerMutation.isPending ? 'Creating account...' : 'Create Account'}
          </Button>
        </form>
        <div className="mt-6 text-center text-sm">
          <span className="text-gray-600">Already have an account? </span>
          <Link to="/login" className="text-amber-600 hover:text-amber-700 font-medium">
            Sign in
          </Link>
        </div>
      </CardContent>
    </Card>
  );
};

export default RegisterPage;
