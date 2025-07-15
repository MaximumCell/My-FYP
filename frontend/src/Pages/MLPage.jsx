import React from 'react';
import { Link } from 'react-router-dom';
import { Cpu, Layers, Tag } from 'lucide-react'; // Importing icons

const MLPage = () => {
  return (
    <div className="bg-gray-100 min-h-screen py-10">
      <div className="max-w-4xl mx-auto bg-white shadow-md rounded-lg overflow-hidden">
        <div className="px-8 py-6">
          <h1 className="text-3xl font-bold text-blue-600 text-center mb-6">
            <Cpu className="inline-block mr-2 -mt-1 w-8 h-8" /> Explore Machine Learning Models
          </h1>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-green-500 mb-4">Understanding Machine Learning</h2>
            <p className="text-gray-700 leading-relaxed mb-4">
              Machine learning (ML) is a field of artificial intelligence (AI) that enables computers to learn from data without being explicitly programmed. It focuses on developing algorithms that can automatically identify patterns in data, make predictions, or make decisions.
            </p>
            <p className="text-gray-700 leading-relaxed mb-4">
              There are various types of machine learning models, each suited for different kinds of tasks and data. Two fundamental categories are Regression and Classification.
            </p>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-indigo-500 mb-4">
              <Layers className="inline-block mr-2 -mt-1 w-6 h-6" /> Regression Models
            </h2>
            <p className="text-gray-700 leading-relaxed mb-4">
              Regression models are used to predict continuous numerical values. For example, predicting house prices, stock prices, or temperature. These models learn the relationship between input features and a target variable that can take on any value within a range.
            </p>
            <p className="text-gray-700 leading-relaxed mb-4">
              Common regression algorithms include Linear Regression, Ridge Regression, Lasso Regression, Support Vector Regression (SVR), Random Forest Regression, and more.
            </p>
            <Link to="/regression" className="inline-block bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition-colors">
              Go to Regression Models
            </Link>
          </section>

          <section className="mb-8">
            <h2 className="text-2xl font-semibold text-yellow-500 mb-4">
              <Tag className="inline-block mr-2 -mt-1 w-6 h-6" /> Classification Models
            </h2>
            <p className="text-gray-700 leading-relaxed mb-4">
              Classification models are used to predict discrete categories or classes. For example, classifying emails as spam or not spam, identifying images of cats or dogs, or predicting whether a customer will churn. These models learn to assign data points to predefined groups.
            </p>
            <p className="text-gray-700 leading-relaxed mb-4">
              Common classification algorithms include Logistic Regression, Support Vector Machines (SVM), Decision Trees, Random Forest Classification, K-Nearest Neighbors (KNN), and more.
            </p>
            <Link to="/classification" className="inline-block bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded transition-colors">
              Go to Classification Models
            </Link>
          </section>
        </div>

        <footer className="bg-gray-200 py-4 text-center text-gray-600 text-sm">
          &copy; 2025 My Machine Learning Platform
        </footer>
      </div>
    </div>
  );
};

export default MLPage;