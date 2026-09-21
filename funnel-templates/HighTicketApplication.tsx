'use client';

import React, { useState } from 'react';

type FormData = {
  name: string;
  email: string;
  social: string;
  revenue: string;
  bottleneck: string;
};

const REVENUE_TIERS = [
  { value: '2500', label: 'Under $5,000 / mo' },
  { value: '7500', label: '$5,000 - $10,000 / mo' },
  { value: '20000', label: '$10,000 - $30,000 / mo' },
  { value: '50000', label: '$30,000+ / mo' },
];

export default function HighTicketApplication() {
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState<FormData>({
    name: '',
    email: '',
    social: '',
    revenue: '',
    bottleneck: '',
  });

  const handleNext = () => setStep((p) => p + 1);

  const handleRevenueSelect = (value: string) => {
    setFormData((prev) => ({ ...prev, revenue: value }));
    handleNext();
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (parseInt(formData.revenue, 10) < 5000) {
      window.location.href = '/downsell-value-video';
    } else {
      window.location.href = `/book-call?name=${encodeURIComponent(formData.name)}`;
    }
  };

  return (
    <div className="max-w-xl mx-auto bg-neutral-900 border border-neutral-800 p-8 rounded-2xl shadow-2xl text-white">
      <div className="mb-8 bg-neutral-800 h-1.5 rounded-full overflow-hidden">
        <div
          className="bg-amber-500 h-full transition-all duration-300"
          style={{ width: `${(step / 3) * 100}%` }}
        />
      </div>

      {step === 1 && (
        <div className="space-y-4">
          <h2 className="text-2xl font-bold tracking-tight">
            Let&apos;s build your high-ticket infrastructure.
          </h2>
          <input
            className="w-full bg-neutral-950 border border-neutral-800 p-3 rounded-lg focus:border-amber-500 outline-none"
            placeholder="Full Name"
            value={formData.name}
            onChange={(e) => setFormData((prev) => ({ ...prev, name: e.target.value }))}
          />
          <input
            className="w-full bg-neutral-950 border border-neutral-800 p-3 rounded-lg focus:border-amber-500 outline-none"
            placeholder="Email Address"
            type="email"
            value={formData.email}
            onChange={(e) => setFormData((prev) => ({ ...prev, email: e.target.value }))}
          />
          <input
            className="w-full bg-neutral-950 border border-neutral-800 p-3 rounded-lg focus:border-amber-500 outline-none"
            placeholder="Social Link (YouTube, Newsletter, etc.)"
            value={formData.social}
            onChange={(e) => setFormData((prev) => ({ ...prev, social: e.target.value }))}
          />
          <button
            type="button"
            onClick={handleNext}
            disabled={!formData.name || !formData.email}
            className="w-full bg-amber-500 hover:bg-amber-600 disabled:opacity-40 disabled:cursor-not-allowed text-neutral-950 font-semibold p-3 rounded-lg transition"
          >
            Continue
          </button>
        </div>
      )}

      {step === 2 && (
        <div className="space-y-4">
          <h2 className="text-2xl font-bold tracking-tight">
            What is your current monthly business revenue?
          </h2>
          {REVENUE_TIERS.map((tier) => (
            <button
              key={tier.value}
              type="button"
              onClick={() => handleRevenueSelect(tier.value)}
              className="w-full text-left bg-neutral-950 hover:border-amber-500 border border-neutral-800 p-4 rounded-lg transition"
            >
              {tier.label}
            </button>
          ))}
        </div>
      )}

      {step === 3 && (
        <form onSubmit={handleSubmit} className="space-y-4">
          <h2 className="text-2xl font-bold tracking-tight">
            What is the biggest operational bottleneck stopping you from hitting $100k/mo?
          </h2>
          <textarea
            className="w-full bg-neutral-950 border border-neutral-800 p-3 rounded-lg focus:border-amber-500 outline-none h-32"
            placeholder="Describe it in detail..."
            value={formData.bottleneck}
            onChange={(e) => setFormData((prev) => ({ ...prev, bottleneck: e.target.value }))}
          />
          <button
            type="submit"
            disabled={!formData.bottleneck}
            className="w-full bg-amber-500 hover:bg-amber-600 disabled:opacity-40 disabled:cursor-not-allowed text-neutral-950 font-semibold p-3 rounded-lg transition"
          >
            Submit Application &amp; View Calendar
          </button>
        </form>
      )}
    </div>
  );
}
