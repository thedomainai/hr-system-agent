'use client';

import { useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { LayoutGrid } from 'lucide-react';
import { useAppStore } from '@/lib/store/useAppStore';
import { WizardProgress } from './WizardProgress';
import { Step1CompanyInfo } from './Step1CompanyInfo';
import { Step2PolicyStatus } from './Step2PolicyStatus';
import { Step3Challenges } from './Step3Challenges';
import { Step4Culture } from './Step4Culture';
import { Step5Organization } from './Step5Organization';
import type { WizardState, WizardStep } from './types';
import { initialWizardState } from './types';

export function SetupWizard() {
  const router = useRouter();
  const { setCompany, setStep: setAppStep } = useAppStore();
  
  const [wizardState, setWizardState] = useState<WizardState>(initialWizardState);
  const [isLoading, setIsLoading] = useState(false);

  const currentStep = wizardState.currentStep;

  // Navigation handlers
  const goToStep = useCallback((step: WizardStep) => {
    setWizardState((prev) => ({ ...prev, currentStep: step }));
  }, []);

  const nextStep = useCallback(() => {
    setWizardState((prev) => ({
      ...prev,
      currentStep: Math.min(prev.currentStep + 1, 5) as WizardStep,
    }));
  }, []);

  const prevStep = useCallback(() => {
    setWizardState((prev) => ({
      ...prev,
      currentStep: Math.max(prev.currentStep - 1, 1) as WizardStep,
    }));
  }, []);

  // Complete wizard and start project
  const handleComplete = useCallback(async () => {
    setIsLoading(true);

    // Use fixed 'demo' companyId for static export compatibility
    const companyId = 'demo';

    // Determine if user has existing values based on all policies being present
    const hasValues = 
      wizardState.policyStatus.hasGradeSystem === true &&
      wizardState.policyStatus.hasEvaluationSystem === true &&
      wizardState.policyStatus.hasCompensationSystem === true;

    // Save to store with expanded data
    setCompany({
      id: companyId,
      name: wizardState.companyBasicInfo.name,
      employeeCount: parseInt(wizardState.companyBasicInfo.employeeCount),
      industry: wizardState.companyBasicInfo.industry,
      philosophy: wizardState.philosophy,
      hasValues,
      // Extended wizard data (stored in custom fields for future use)
      averageSalary: wizardState.averageSalary ? parseFloat(wizardState.averageSalary) : undefined,
      turnoverRate: wizardState.turnoverRate ? parseFloat(wizardState.turnoverRate) : undefined,
      managerRatio: wizardState.managerRatio ? parseFloat(wizardState.managerRatio) : undefined,
    });

    // Store wizard-specific data in localStorage for persistence
    const wizardData = {
      policyStatus: wizardState.policyStatus,
      challengesInfo: wizardState.challengesInfo,
      cultureInfo: wizardState.cultureInfo,
      organizationInfo: wizardState.organizationInfo,
    };
    localStorage.setItem('hr-wizard-data', JSON.stringify(wizardData));

    setAppStep(1);

    // Navigate based on whether they have values
    if (hasValues) {
      router.push(`/${companyId}/values`);
    } else {
      router.push(`/${companyId}/talent`);
    }
  }, [wizardState, router, setCompany, setAppStep]);

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col items-center justify-center p-4 sm:p-8">
      <div className="max-w-xl w-full">
        {/* Header */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-primary-600 rounded-xl shadow-lg shadow-primary-200 mb-4">
            <LayoutGrid size={24} className="text-white" strokeWidth={2} />
          </div>
          <h1 className="text-2xl font-bold text-slate-900">HR Architect</h1>
          <p className="text-slate-500 mt-2 text-sm">
            高品質な人事制度を、最短で。
          </p>
        </div>

        {/* Main Card */}
        <div className="bg-white rounded-2xl shadow-xl shadow-slate-200/50 p-6 sm:p-8">
          {/* Progress Indicator */}
          <WizardProgress 
            currentStep={currentStep} 
            onStepClick={goToStep}
          />

          {/* Step Content */}
          <div className="min-h-[400px]">
            {currentStep === 1 && (
              <Step1CompanyInfo
                data={wizardState.companyBasicInfo}
                onChange={(data) =>
                  setWizardState((prev) => ({ ...prev, companyBasicInfo: data }))
                }
                onNext={nextStep}
              />
            )}

            {currentStep === 2 && (
              <Step2PolicyStatus
                data={wizardState.policyStatus}
                onChange={(data) =>
                  setWizardState((prev) => ({ ...prev, policyStatus: data }))
                }
                onNext={nextStep}
                onBack={prevStep}
              />
            )}

            {currentStep === 3 && (
              <Step3Challenges
                data={wizardState.challengesInfo}
                policyStatus={wizardState.policyStatus}
                onChange={(data) =>
                  setWizardState((prev) => ({ ...prev, challengesInfo: data }))
                }
                onNext={nextStep}
                onBack={prevStep}
              />
            )}

            {currentStep === 4 && (
              <Step4Culture
                data={wizardState.cultureInfo}
                onChange={(data) =>
                  setWizardState((prev) => ({ ...prev, cultureInfo: data }))
                }
                onNext={nextStep}
                onBack={prevStep}
              />
            )}

            {currentStep === 5 && (
              <Step5Organization
                data={wizardState.organizationInfo}
                onChange={(data) =>
                  setWizardState((prev) => ({ ...prev, organizationInfo: data }))
                }
                onComplete={handleComplete}
                onBack={prevStep}
                isLoading={isLoading}
              />
            )}
          </div>
        </div>

        {/* Footer hint */}
        <p className="text-center text-xs text-slate-400 mt-4">
          入力した情報は人事制度設計の参考に使用されます
        </p>
      </div>
    </div>
  );
}
