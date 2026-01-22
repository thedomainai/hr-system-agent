'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  useAppStore,
  TraitCard as TraitCardType,
  TalentPersona
} from '@/lib/store/useAppStore';
import { Button } from '@/components/ui/Button';
import {
  ArrowRight,
  Star,
  Sparkles,
  Zap,
  Shield,
  Users,
  Trophy,
  Heart,
  Brain,
  Activity,
  Eye,
  User,
  ChevronRight,
  Edit3,
  X,
  Check
} from 'lucide-react';
import { cn } from '@/lib/utils/cn';

// Culture keywords for selection
const CULTURE_KEYWORDS = [
  { id: 'innovation', label: '革新・挑戦', icon: Zap, desc: '新しい価値の創造を重視' },
  { id: 'stability', label: '規律・安定', icon: Shield, desc: '確実な遂行と安定を重視' },
  { id: 'customer', label: '顧客志向', icon: Heart, desc: '顧客への価値提供を最優先' },
  { id: 'teamwork', label: 'チームワーク', icon: Users, desc: '個よりチームの成果を重視' },
  { id: 'performance', label: '成果主義', icon: Trophy, desc: '結果と数字へのこだわり' },
  { id: 'autonomy', label: '自律・自由', icon: Star, desc: '個人の裁量と責任を尊重' },
];

// Layer configuration for display
const LAYER_CONFIG = {
  psychological: {
    label: '心理特性',
    icon: Brain,
    color: 'purple',
    bgColor: 'bg-purple-50',
    borderColor: 'border-purple-200',
    iconBg: 'bg-purple-100',
    iconColor: 'text-purple-600',
    activeBorder: 'border-purple-500',
  },
  behavioral: {
    label: '行動特性',
    icon: Activity,
    color: 'blue',
    bgColor: 'bg-blue-50',
    borderColor: 'border-blue-200',
    iconBg: 'bg-blue-100',
    iconColor: 'text-blue-600',
    activeBorder: 'border-blue-500',
  },
  surface: {
    label: '表面化した行動',
    icon: Eye,
    color: 'green',
    bgColor: 'bg-green-50',
    borderColor: 'border-green-200',
    iconBg: 'bg-green-100',
    iconColor: 'text-green-600',
    activeBorder: 'border-green-500',
  },
};

// Trait card component
interface TraitCardProps {
  trait: TraitCardType;
  layerType: 'psychological' | 'behavioral' | 'surface';
  isSelected: boolean;
  onClick: () => void;
}

function TraitCard({ trait, layerType, isSelected, onClick }: TraitCardProps) {
  const config = LAYER_CONFIG[layerType];

  return (
    <button
      onClick={onClick}
      className={cn(
        "w-full p-3 rounded-lg border-2 text-left transition-all",
        config.bgColor,
        isSelected ? config.activeBorder : config.borderColor,
        isSelected && "shadow-md ring-2 ring-offset-2",
        isSelected && layerType === 'psychological' && "ring-purple-300",
        isSelected && layerType === 'behavioral' && "ring-blue-300",
        isSelected && layerType === 'surface' && "ring-green-300",
        "hover:shadow-sm"
      )}
    >
      <h4 className="font-semibold text-slate-800 text-sm">{trait.name}</h4>
      <p className="text-xs text-slate-600 mt-1 line-clamp-2">{trait.description}</p>
    </button>
  );
}

// Editor panel component
interface EditorPanelProps {
  selectedCard: {
    personaId: string;
    layerType: 'psychological' | 'behavioral' | 'surface' | 'persona';
    card?: TraitCardType;
    personaSummary?: string;
  } | null;
  onClose: () => void;
  onSave: (updates: { name?: string; description?: string; summary?: string }) => void;
}

function EditorPanel({ selectedCard, onClose, onSave }: EditorPanelProps) {
  const [editName, setEditName] = useState('');
  const [editDescription, setEditDescription] = useState('');
  const [editSummary, setEditSummary] = useState('');

  // Initialize form when selection changes
  useEffect(() => {
    if (selectedCard?.card) {
      setEditName(selectedCard.card.name);
      setEditDescription(selectedCard.card.description);
    } else if (selectedCard?.personaSummary) {
      setEditSummary(selectedCard.personaSummary);
    }
  }, [selectedCard]);

  if (!selectedCard) {
    return (
      <div className="h-full flex items-center justify-center text-slate-400">
        <div className="text-center">
          <Edit3 size={40} className="mx-auto mb-3 opacity-50" />
          <p className="text-sm">カードをクリックして編集</p>
        </div>
      </div>
    );
  }

  const isPersonaEdit = selectedCard.layerType === 'persona';
  const config = isPersonaEdit ? null : LAYER_CONFIG[selectedCard.layerType as keyof typeof LAYER_CONFIG];

  const handleSave = () => {
    if (isPersonaEdit) {
      onSave({ summary: editSummary });
    } else {
      onSave({ name: editName, description: editDescription });
    }
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-slate-200">
        <div className="flex items-center gap-2">
          {config && (
            <div className={cn("p-1.5 rounded-lg", config.iconBg)}>
              <config.icon size={16} className={config.iconColor} />
            </div>
          )}
          {isPersonaEdit && (
            <div className="p-1.5 rounded-lg bg-indigo-100">
              <User size={16} className="text-indigo-600" />
            </div>
          )}
          <span className="font-semibold text-slate-800">
            {isPersonaEdit ? '人材像を編集' : `${config?.label}を編集`}
          </span>
        </div>
        <button
          onClick={onClose}
          className="p-1 rounded hover:bg-slate-100 text-slate-400 hover:text-slate-600"
        >
          <X size={18} />
        </button>
      </div>

      {/* Form */}
      <div className="flex-1 p-4 space-y-4 overflow-auto">
        {isPersonaEdit ? (
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1.5">
              人材像の説明
            </label>
            <textarea
              value={editSummary || selectedCard.personaSummary || ''}
              onChange={(e) => setEditSummary(e.target.value)}
              rows={6}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm resize-none"
              placeholder="統合された人材像の説明を入力..."
            />
          </div>
        ) : (
          <>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">
                名称
              </label>
              <input
                type="text"
                value={editName || selectedCard.card?.name || ''}
                onChange={(e) => setEditName(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm"
                placeholder="特性の名称"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1.5">
                説明
              </label>
              <textarea
                value={editDescription || selectedCard.card?.description || ''}
                onChange={(e) => setEditDescription(e.target.value)}
                rows={4}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent text-sm resize-none"
                placeholder="特性の説明を入力..."
              />
            </div>
          </>
        )}
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-slate-200">
        <Button onClick={handleSave} className="w-full" icon={<Check size={16} />}>
          変更を保存
        </Button>
      </div>
    </div>
  );
}

// Main page component
export default function TalentPage({ params }: { params: { companyId: string } }) {
  const router = useRouter();
  const {
    talentProfileV2,
    generateTalentProfileV2,
    updateTraitCard,
    updatePersonaSummary,
    generateGrading,
    setStep
  } = useAppStore();

  const [mode, setMode] = useState<'selection' | 'generating' | 'review'>('selection');
  const [selectedKeywords, setSelectedKeywords] = useState<string[]>([]);
  const [activePersonaIndex, setActivePersonaIndex] = useState(0);
  const [selectedCard, setSelectedCard] = useState<{
    personaId: string;
    layerType: 'psychological' | 'behavioral' | 'surface' | 'persona';
    card?: TraitCardType;
    cardId?: string;
    personaSummary?: string;
  } | null>(null);

  // Selection Logic
  const toggleKeyword = (id: string) => {
    if (selectedKeywords.includes(id)) {
      setSelectedKeywords(prev => prev.filter(k => k !== id));
    } else {
      if (selectedKeywords.length < 3) {
        setSelectedKeywords(prev => [...prev, id]);
      }
    }
  };

  const handleGenerate = async () => {
    setMode('generating');
    await generateTalentProfileV2(selectedKeywords);
    setMode('review');
  };

  const handleNext = async () => {
    await generateGrading();
    setStep(3);
    router.push(`/${params.companyId}/grading`);
  };

  const handleCardSelect = (
    personaId: string,
    layerType: 'psychological' | 'behavioral' | 'surface' | 'persona',
    card?: TraitCardType,
    cardId?: string,
    personaSummary?: string
  ) => {
    setSelectedCard({ personaId, layerType, card, cardId, personaSummary });
  };

  const handleEditorSave = (updates: { name?: string; description?: string; summary?: string }) => {
    if (!selectedCard) return;

    if (selectedCard.layerType === 'persona' && updates.summary) {
      updatePersonaSummary(selectedCard.personaId, updates.summary);
    } else if (selectedCard.cardId && (updates.name || updates.description)) {
      updateTraitCard(
        selectedCard.personaId,
        selectedCard.layerType as 'psychological' | 'behavioral' | 'surface',
        selectedCard.cardId,
        {
          name: updates.name || selectedCard.card?.name || '',
          description: updates.description || selectedCard.card?.description || ''
        }
      );
    }
    setSelectedCard(null);
  };

  // --- Render: Selection Step ---
  if (mode === 'selection') {
    return (
      <div className="max-w-3xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-slate-900">組織カルチャーの定義</h2>
          <p className="text-slate-500 mt-2">
            貴社が大切にしている価値観や、社員に求める要素を最大3つ選んでください。<br/>
            AIがこれをもとに「求める人材像」を定義します。
          </p>
        </div>

        <div className="flex flex-col gap-3 max-w-md mx-auto">
          {CULTURE_KEYWORDS.map((item) => {
            const isSelected = selectedKeywords.includes(item.id);
            return (
              <button
                key={item.id}
                onClick={() => toggleKeyword(item.id)}
                className={cn(
                  "p-4 rounded-xl border-2 text-left transition-all relative overflow-hidden group flex items-center gap-4",
                  isSelected
                    ? "border-primary-500 bg-primary-50 shadow-md"
                    : "border-slate-200 bg-white hover:border-primary-200 hover:bg-slate-50"
                )}
              >
                <div className={cn(
                  "w-10 h-10 rounded-lg flex items-center justify-center shrink-0 transition-colors",
                  isSelected ? "bg-primary-500 text-white" : "bg-slate-100 text-slate-400 group-hover:text-primary-500"
                )}>
                  <item.icon size={20} />
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className={cn("font-bold", isSelected ? "text-primary-900" : "text-slate-800")}>
                    {item.label}
                  </h3>
                  <p className="text-xs text-slate-500">{item.desc}</p>
                </div>
                {isSelected && (
                  <div className="w-6 h-6 bg-primary-500 rounded-full flex items-center justify-center shrink-0">
                    <Star size={14} className="text-white" fill="currentColor" />
                  </div>
                )}
              </button>
            );
          })}
        </div>

        <div className="flex justify-center pt-4">
          <Button
            onClick={handleGenerate}
            disabled={selectedKeywords.length === 0}
            className="w-full max-w-sm h-12 text-base"
            icon={<Sparkles size={18} />}
          >
            人材像を生成する ({selectedKeywords.length}/3)
          </Button>
        </div>
      </div>
    );
  }

  // --- Render: Generating Step ---
  if (mode === 'generating') {
    return (
      <div className="flex flex-col items-center justify-center h-96 space-y-6 animate-in fade-in duration-500">
        <div className="relative">
          <div className="absolute inset-0 bg-primary-200 rounded-full blur-xl animate-pulse"></div>
          <div className="relative bg-white p-6 rounded-full shadow-lg">
            <Sparkles size={40} className="text-primary-500 animate-spin-slow" />
          </div>
        </div>
        <div className="text-center space-y-2">
          <h3 className="text-xl font-bold text-slate-900">人材像をデザイン中...</h3>
          <p className="text-slate-500">
            選択されたカルチャーキーワードと企業理念を分析し、<br/>
            4層構造の人材像を構築しています。
          </p>
        </div>
      </div>
    );
  }

  // --- Render: Review Step (New 4-Layer Structure) ---
  if (!talentProfileV2) return null;

  const activePersona = talentProfileV2.personas[activePersonaIndex];

  return (
    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Header */}
      <div className="flex items-end justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">求める人材像</h2>
          <p className="text-slate-500 mt-1">
            選択されたカルチャーに基づき、3つの人材像を定義しました。各項目はクリックして編集できます。
          </p>
        </div>
        <Button onClick={handleNext} icon={<ArrowRight size={18} />}>
          承認して次へ
        </Button>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 mb-6">
        {talentProfileV2.personas.map((persona, index) => (
          <button
            key={persona.id}
            onClick={() => {
              setActivePersonaIndex(index);
              setSelectedCard(null);
            }}
            className={cn(
              "flex-1 px-4 py-3 rounded-xl border-2 transition-all",
              activePersonaIndex === index
                ? "border-indigo-500 bg-indigo-50 shadow-md"
                : "border-slate-200 bg-white hover:border-indigo-200"
            )}
          >
            <div className="flex items-center justify-center gap-2">
              <div className={cn(
                "w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold",
                activePersonaIndex === index
                  ? "bg-indigo-500 text-white"
                  : "bg-slate-200 text-slate-600"
              )}>
                {index + 1}
              </div>
              <span className={cn(
                "font-semibold",
                activePersonaIndex === index ? "text-indigo-900" : "text-slate-700"
              )}>
                {persona.name}
              </span>
            </div>
          </button>
        ))}
      </div>

      {/* Main Content - Horizontal Layout */}
      <div className="flex gap-6 items-stretch">
        {/* Section 1: 特性 */}
        <div className="flex-1 bg-white rounded-2xl border border-slate-200 p-6">
          <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-4">
            特性
          </h3>

          <div className="flex gap-4">
            {/* 背景にある心理特性 */}
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-3">
                <div className={cn("p-1.5 rounded-lg", LAYER_CONFIG.psychological.iconBg)}>
                  <Brain size={16} className={LAYER_CONFIG.psychological.iconColor} />
                </div>
                <span className="font-semibold text-slate-700 text-sm">
                  背景にある心理特性
                </span>
              </div>
              <div className="space-y-2">
                {activePersona.psychologicalTraits.map((trait) => (
                  <TraitCard
                    key={trait.id}
                    trait={trait}
                    layerType="psychological"
                    isSelected={selectedCard?.cardId === trait.id}
                    onClick={() => handleCardSelect(activePersona.id, 'psychological', trait, trait.id)}
                  />
                ))}
              </div>
            </div>

            {/* 背景にある行動特性 */}
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-3">
                <div className={cn("p-1.5 rounded-lg", LAYER_CONFIG.behavioral.iconBg)}>
                  <Activity size={16} className={LAYER_CONFIG.behavioral.iconColor} />
                </div>
                <span className="font-semibold text-slate-700 text-sm">
                  背景にある行動特性
                </span>
              </div>
              <div className="space-y-2">
                {activePersona.behavioralTraits.map((trait) => (
                  <TraitCard
                    key={trait.id}
                    trait={trait}
                    layerType="behavioral"
                    isSelected={selectedCard?.cardId === trait.id}
                    onClick={() => handleCardSelect(activePersona.id, 'behavioral', trait, trait.id)}
                  />
                ))}
              </div>
            </div>

            {/* 表面化した行動 */}
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-3">
                <div className={cn("p-1.5 rounded-lg", LAYER_CONFIG.surface.iconBg)}>
                  <Eye size={16} className={LAYER_CONFIG.surface.iconColor} />
                </div>
                <span className="font-semibold text-slate-700 text-sm">
                  表面化した行動
                </span>
              </div>
              <div className="space-y-2">
                {activePersona.surfaceBehaviors.map((trait) => (
                  <TraitCard
                    key={trait.id}
                    trait={trait}
                    layerType="surface"
                    isSelected={selectedCard?.cardId === trait.id}
                    onClick={() => handleCardSelect(activePersona.id, 'surface', trait, trait.id)}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Section 2: 人材像 */}
        <div className="w-72 flex">
          <button
            onClick={() => handleCardSelect(
              activePersona.id,
              'persona',
              undefined,
              undefined,
              activePersona.personaSummary
            )}
            className={cn(
              "w-full bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl p-5 text-white shadow-lg text-left transition-all flex flex-col",
              selectedCard?.layerType === 'persona' && selectedCard?.personaId === activePersona.id
                && "ring-4 ring-offset-2 ring-indigo-300"
            )}
          >
            <div className="flex items-center gap-2 mb-3">
              <div className="bg-white/20 p-2 rounded-lg">
                <User size={18} className="text-white" />
              </div>
              <h3 className="font-bold text-sm uppercase tracking-wide text-white/80">人材像</h3>
            </div>
            <p className="text-white/90 text-sm leading-relaxed flex-1">
              {activePersona.personaSummary}
            </p>
            <div className="flex justify-end mt-3">
              <Edit3 size={14} className="text-white/50" />
            </div>
          </button>
        </div>
      </div>

      {/* Bottom: Editor Panel */}
      {selectedCard && (
        <div className="mt-6 bg-white rounded-2xl border border-slate-200 overflow-hidden animate-in fade-in slide-in-from-bottom-2 duration-200">
          <div className="max-w-2xl mx-auto">
            <EditorPanel
              selectedCard={selectedCard}
              onClose={() => setSelectedCard(null)}
              onSave={handleEditorSave}
            />
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="text-center pt-6">
        <button
          onClick={() => {
            setMode('selection');
            setSelectedCard(null);
          }}
          className="text-sm text-slate-400 hover:text-slate-600 underline"
        >
          条件を変更して再生成する
        </button>
      </div>
    </div>
  );
}
