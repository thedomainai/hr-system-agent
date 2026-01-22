'use client';

import { FileText, Edit3 } from 'lucide-react';
import { useWorkspaceStore } from '@/lib/store/workspaceStore';
import type { DocumentData } from '@/types';

function generateMarkdown(data: DocumentData): string {
  return `# 人事制度基本規定

DRAFT v0.4 - 2026.04.01 施行予定

## 第1章 総則

### 第1条（目的）
本規定は、社員の能力および業績を公正に評価し、それに基づいた処遇を行うことで、社員の意欲向上と会社の発展を図ることを目的とする。

### 第2条（人事理念）
${data.philosophy || '（方針策定フェーズにて定義されます...）'}

## 第2章 等級制度

### 第X条（等級区分）
${
  data.gradeList.length > 0
    ? data.gradeList.map((g) => `- ${g.name}: ${g.desc}`).join('\n')
    : '（等級設計フェーズにて定義されます...）'
}
`;
}

export function DocumentPanel() {
  const { documentData, isEditing, setEditing } = useWorkspaceStore();

  return (
    <div className="bg-white h-full flex flex-col shadow-2xl shadow-slate-200/50 relative z-10">
      {/* Toolbar */}
      <div className="px-6 py-4 flex justify-between items-center bg-white z-10 border-b border-slate-100">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-primary-50 text-primary-600 rounded-lg">
            <FileText size={18} />
          </div>
          <div>
            <h3 className="text-sm font-bold text-slate-800">
              人事制度規定案.md
            </h3>
            <p className="text-[10px] text-slate-400 font-medium flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-green-500" /> Saved
              locally
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setEditing(!isEditing)}
            className={`p-2 rounded-lg transition-colors ${
              isEditing
                ? 'bg-primary-100 text-primary-600'
                : 'text-slate-400 hover:bg-slate-50'
            }`}
            title={isEditing ? 'プレビューに戻る' : '編集する'}
          >
            <Edit3 size={18} />
          </button>
        </div>
      </div>

      {/* Editor/Preview Area */}
      <div className="flex-1 overflow-y-auto bg-slate-50/30 scrollbar-thin">
        <div className="max-w-[210mm] mx-auto bg-white min-h-full p-12 shadow-sm my-8">
          {isEditing ? (
            <textarea
              className="w-full h-full min-h-[600px] resize-none outline-none font-mono text-sm text-slate-700 leading-relaxed bg-transparent"
              defaultValue={generateMarkdown(documentData)}
            />
          ) : (
            <DocumentPreview data={documentData} />
          )}
        </div>
      </div>
    </div>
  );
}

function DocumentPreview({ data }: { data: DocumentData }) {
  return (
    <div className="space-y-10 text-slate-800 font-serif">
      {/* Title */}
      <div className="text-center pb-8 border-b-2 border-slate-100/50">
        <h1 className="text-3xl font-bold mb-3 tracking-tight text-slate-900">
          人事制度基本規定
        </h1>
        <div className="flex justify-center gap-4 text-xs text-slate-400 font-sans">
          <span>DRAFT v0.4</span>
          <span>-</span>
          <span>2026.04.01 施行予定</span>
        </div>
      </div>

      {/* Chapter 1 */}
      <section>
        <h2 className="text-lg font-bold text-slate-900 mb-6 flex items-center gap-3">
          <span className="flex items-center justify-center w-6 h-6 rounded bg-slate-900 text-white text-xs font-sans">
            1
          </span>
          総則
        </h2>
        <div className="space-y-6 text-sm leading-8 text-slate-700">
          <div className="pl-4 border-l-2 border-slate-100 hover:border-primary-200 transition-colors">
            <h3 className="font-bold text-slate-900 mb-1">第1条（目的）</h3>
            <p>
              本規定は、社員の能力および業績を公正に評価し、それに基づいた処遇を行うことで、社員の意欲向上と会社の発展を図ることを目的とする。
            </p>
          </div>
          <div
            className={`p-6 rounded-xl transition-all duration-500 ${
              data.philosophy ? 'bg-primary-50/30' : 'bg-slate-50'
            }`}
          >
            <h3 className="font-bold text-slate-900 mb-2">第2条（人事理念）</h3>
            {data.philosophy ? (
              <p className="text-slate-800">{data.philosophy}</p>
            ) : (
              <span className="text-slate-400 italic font-sans text-xs">
                Waiting for input...
              </span>
            )}
          </div>
        </div>
      </section>

      {/* Chapter 2 */}
      <section>
        <h2 className="text-lg font-bold text-slate-900 mb-6 flex items-center gap-3">
          <span className="flex items-center justify-center w-6 h-6 rounded bg-slate-900 text-white text-xs font-sans">
            2
          </span>
          等級制度
        </h2>
        <div className="p-6 rounded-xl bg-slate-50">
          {data.gradeType ? (
            <table className="w-full text-left text-xs font-sans">
              <thead className="text-slate-500 uppercase tracking-wider border-b border-slate-200">
                <tr>
                  <th className="p-3">Grade</th>
                  <th className="p-3">Definition</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {data.gradeList.map((g, i) => (
                  <tr key={i}>
                    <td className="p-3 font-bold text-primary-900">{g.name}</td>
                    <td className="p-3 text-slate-600">{g.desc}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <span className="text-slate-400 italic font-sans text-xs">
              Waiting for input...
            </span>
          )}
        </div>
      </section>
    </div>
  );
}
