// Educational Web App MVP - Interactive Module Viewer & Quiz Player
'use client';
import React, { useState } from 'react';

interface QuizQuestion {
  question: string;
  options: string[];
  correctIndex: number;
}

export default function EducationalModulePlayer() {
  const [currentStep, setCurrentStep] = useState(0);
  const [selectedOption, setSelectedOption] = useState<number | null>(null);
  const [score, setScore] = useState(0);

  const questions: QuizQuestion[] = [
    {
      question: "¿Cuál es el principio fundamental de la ley de conservación de energía?",
      options: [
        "La energía se crea espontáneamente",
        "La energía no se crea ni se destruye, solo se transforma",
        "La energía desaparece con la fricción"
      ],
      correctIndex: 1
    }
  ];

  const handleSelect = (idx: number) => {
    setSelectedOption(idx);
    if (idx === questions[currentStep].correctIndex) {
      setScore(score + 1);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-xl shadow-lg border border-slate-100">
      <div className="flex justify-between items-center mb-6">
        <span className="text-sm font-semibold uppercase text-indigo-600 tracking-wider">Módulo 1: Física</span>
        <span className="text-sm font-bold text-slate-500">Puntaje: {score} pts</span>
      </div>
      <h2 className="text-xl font-bold text-slate-800 mb-4">{questions[currentStep].question}</h2>
      <div className="space-y-3">
        {questions[currentStep].options.map((opt, i) => (
          <button
            key={i}
            onClick={() => handleSelect(i)}
            className={`w-full text-left p-4 rounded-lg border transition-all ${
              selectedOption === i ? 'border-indigo-600 bg-indigo-50 font-semibold' : 'border-slate-200 hover:bg-slate-50'
            }`}
          >
            {opt}
          </button>
        ))}
      </div>
    </div>
  );
}
