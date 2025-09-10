import React from "react";
import { Link } from "react-router-dom";
import { Cpu, Layers, Tag, Activity, Zap } from "lucide-react";

const FeatureCard = ({ icon: Icon, title, desc, to, accent }) => (
  <Link to={to} className="group">
    <div className="bg-slate-800/50 dark:bg-slate-900/50 backdrop-blur-sm border border-slate-700/30 rounded-2xl p-8 min-h-[150px] flex items-start gap-6 hover:shadow-xl transition-shadow">
      <div
        className={`flex-none rounded-lg w-12 h-12 flex items-center justify-center ${accent}`}
      >
        <Icon className="w-6 h-6 text-white" />
      </div>
      <div className="flex-1">
        <h3 className="text-2xl font-semibold text-slate-100">{title}</h3>
        <p className="mt-2 text-slate-200/80 leading-relaxed">{desc}</p>
        <div className="mt-6">
          <span className="text-sm font-medium text-white/90 group-hover:underline">
            Open
          </span>
        </div>
      </div>
    </div>
  </Link>
);

const MLPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-900/90 to-slate-800 text-slate-100 py-16">
      <div className="max-w-6xl mx-auto px-6">
        <header className="text-center mb-12">
          <div className="inline-flex items-center gap-4 bg-gradient-to-r from-slate-800/30 to-slate-700/10 px-6 py-4 rounded-full">
            <Cpu className="w-10 h-10 text-blue-400" />
            <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight">
              ML Lab
            </h1>
          </div>
          <p className="mt-6 max-w-3xl mx-auto text-slate-300">
            Train, evaluate, and deploy models quickly — from classic regression
            and classification to deep learning image models. Use the Auto-Train
            feature to compare candidates and pick the best pipeline.
          </p>
        </header>

        <section className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <FeatureCard
            icon={Layers}
            title="Regression"
            desc="Predict continuous targets with linear, tree-based and ensemble methods. Includes CV and exportable pipelines."
            to="/regression"
            accent="bg-blue-600/80"
          />

          <FeatureCard
            icon={Tag}
            title="Classification"
            desc="Build and evaluate classifiers with rich metrics and confusion matrices. Export deployable pipelines."
            to="/classification"
            accent="bg-amber-600/80"
          />

          <FeatureCard
            icon={Activity}
            title="Deep Learning"
            desc="Train CNNs and MLPs for images and tabular data. Supports training logs and model downloads."
            to="/deep"
            accent="bg-indigo-600/80"
          />

          <FeatureCard
            icon={Zap}
            title="Auto-Train"
            desc="Auto-select the best pipeline by speed and accuracy, optionally tune hyperparameters."
            to="/auto_train"
            accent="bg-amber-500/80"
          />
        </section>

        <section className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="md:col-span-2 bg-slate-800/40 backdrop-blur-sm border border-slate-700/30 rounded-2xl p-8">
            <h2 className="text-2xl font-semibold mb-3 text-slate-100">
              A little about models
            </h2>
            <p className="text-slate-300 leading-relaxed">
              Each model type exposes a simple pipeline: data ingestion (CSV),
              preprocessing (scaling, encoding), model training, evaluation, and
              model export. After training you can inspect feature importances
              (where available), download the serialized pipeline, or test
              predictions using sample inputs from the UI.
            </p>
            <ul className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-4 text-sm text-slate-300">
              <li>Cross-validation & hyperparameter search</li>
              <li>Model explainability (feature importances)</li>
              <li>Download trained model artifacts</li>
            </ul>
          </div>

          <div className="bg-slate-800/30 backdrop-blur-sm border border-slate-700/20 rounded-2xl p-8 flex flex-col justify-center">
            <h3 className="text-lg font-semibold text-slate-100">
              Ready to start?
            </h3>
            <p className="mt-2 text-slate-300 text-sm">
              Upload a CSV, pick a model type and start training. Models are
              exportable after training.
            </p>
            <div className="mt-4">
              <Link
                to="/upload"
                className="inline-block bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md"
              >
                Upload CSV
              </Link>
            </div>
          </div>
        </section>

        <footer className="mt-12 text-center text-sm text-slate-400">
          &copy; 2025 My Machine Learning Platform
        </footer>
      </div>
    </div>
  );
};

export default MLPage;
