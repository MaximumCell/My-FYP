import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
from collections import Counter

def analyze_data_quality(file, target_column: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze uploaded data to provide preview and quality insights.
    
    Args:
        file: Uploaded file object
        target_column: Optional target column name for classification analysis
        
    Returns:
        Dictionary containing data preview, stats, and quality warnings
    """
    try:
        # Read the data
        df = pd.read_csv(file)
        
        # Reset file pointer for future use
        file.seek(0)
        
        # Basic info
        n_rows, n_cols = df.shape
        
        # Data preview (first 10 rows)
        preview_data = df.head(10).to_dict('records')
        
        # Column information
        columns_info = []
        for col in df.columns:
            col_info = {
                'name': col,
                'dtype': str(df[col].dtype),
                'non_null_count': int(df[col].count()),
                'null_count': int(df[col].isnull().sum()),
                'unique_count': int(df[col].nunique()),
                'sample_values': df[col].dropna().head(5).tolist()
            }
            
            # Add type-specific statistics
            if df[col].dtype in ['int64', 'float64']:
                col_info.update({
                    'mean': float(df[col].mean()) if not df[col].isnull().all() else None,
                    'std': float(df[col].std()) if not df[col].isnull().all() else None,
                    'min': float(df[col].min()) if not df[col].isnull().all() else None,
                    'max': float(df[col].max()) if not df[col].isnull().all() else None
                })
            elif df[col].dtype == 'object':
                # For categorical/text columns
                value_counts = df[col].value_counts().head(5)
                col_info['top_values'] = value_counts.to_dict()
                
            columns_info.append(col_info)
        
        # Data quality warnings
        warnings = []
        
        # Check for missing data
        missing_percentage = (df.isnull().sum() / len(df) * 100).round(2)
        high_missing_cols = missing_percentage[missing_percentage > 20].to_dict()
        if high_missing_cols:
            warnings.append({
                'type': 'missing_data',
                'severity': 'warning',
                'message': f"High missing data: {list(high_missing_cols.keys())}",
                'details': high_missing_cols
            })
        
        # Check for high cardinality categorical columns
        categorical_cols = df.select_dtypes(include=['object']).columns
        high_cardinality_cols = []
        for col in categorical_cols:
            unique_ratio = df[col].nunique() / len(df)
            if unique_ratio > 0.5 and df[col].nunique() > 10:
                high_cardinality_cols.append({
                    'column': col,
                    'unique_count': int(df[col].nunique()),
                    'unique_ratio': round(unique_ratio, 3)
                })
        
        if high_cardinality_cols:
            warnings.append({
                'type': 'high_cardinality',
                'severity': 'warning',
                'message': "High cardinality categorical columns detected",
                'details': high_cardinality_cols
            })
        
        # Check for duplicate rows
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            warnings.append({
                'type': 'duplicates',
                'severity': 'info',
                'message': f"Found {duplicates} duplicate rows ({duplicates/len(df)*100:.1f}%)",
                'details': {'count': int(duplicates), 'percentage': round(duplicates/len(df)*100, 2)}
            })
        
        # Target column specific analysis
        target_analysis = None
        if target_column and target_column in df.columns:
            target_analysis = analyze_target_column(df, target_column, warnings)
        
        return {
            'success': True,
            'data_info': {
                'n_rows': n_rows,
                'n_cols': n_cols,
                'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB"
            },
            'preview': preview_data,
            'columns': columns_info,
            'target_analysis': target_analysis,
            'warnings': warnings,
            'recommendations': generate_recommendations(df, warnings, target_column)
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"Error analyzing data: {str(e)}"
        }

def analyze_target_column(df: pd.DataFrame, target_column: str, warnings: List[Dict]) -> Dict[str, Any]:
    """Analyze the target column for classification insights."""
    target_series = df[target_column]
    
    # Class distribution
    class_counts = target_series.value_counts().to_dict()
    total_samples = len(target_series.dropna())
    
    # Calculate class percentages
    class_percentages = {k: round(v/total_samples*100, 2) for k, v in class_counts.items()}
    
    # Check for class imbalance
    if len(class_counts) > 1:
        min_class_pct = min(class_percentages.values())
        max_class_pct = max(class_percentages.values())
        imbalance_ratio = min_class_pct / max_class_pct
        
        if imbalance_ratio < 0.1:
            warnings.append({
                'type': 'severe_class_imbalance',
                'severity': 'error',
                'message': f"Severe class imbalance in target '{target_column}' (ratio: {imbalance_ratio:.1%})",
                'details': {
                    'class_percentages': class_percentages,
                    'imbalance_ratio': round(imbalance_ratio, 3),
                    'recommendation': 'Consider using class weights, resampling techniques, or stratified sampling'
                }
            })
        elif imbalance_ratio < 0.3:
            warnings.append({
                'type': 'moderate_class_imbalance',
                'severity': 'warning',
                'message': f"Moderate class imbalance in target '{target_column}' (ratio: {imbalance_ratio:.1%})",
                'details': {
                    'class_percentages': class_percentages,
                    'imbalance_ratio': round(imbalance_ratio, 3),
                    'recommendation': 'Consider using balanced metrics like F1-score or class weights'
                }
            })
    
    # Check number of classes
    n_classes = len(class_counts)
    if n_classes > 20:
        warnings.append({
            'type': 'too_many_classes',
            'severity': 'warning',
            'message': f"Target column has {n_classes} classes - consider grouping or using regression",
            'details': {'n_classes': n_classes}
        })
    elif n_classes == 1:
        warnings.append({
            'type': 'single_class',
            'severity': 'error',
            'message': "Target column has only one class - classification not possible",
            'details': {'unique_value': list(class_counts.keys())[0]}
        })
    
    return {
        'column': target_column,
        'n_classes': n_classes,
        'class_counts': class_counts,
        'class_percentages': class_percentages,
        'missing_values': int(target_series.isnull().sum()),
        'data_type': str(target_series.dtype)
    }

def generate_recommendations(df: pd.DataFrame, warnings: List[Dict], target_column: Optional[str] = None) -> List[Dict[str, str]]:
    """Generate actionable recommendations based on data analysis."""
    recommendations = []
    
    # Data size recommendations
    n_rows, n_cols = df.shape
    if n_rows < 100:
        recommendations.append({
            'type': 'data_size',
            'priority': 'high',
            'message': f"Dataset is small ({n_rows} rows). Consider collecting more data for better model performance."
        })
    elif n_rows < 1000:
        recommendations.append({
            'type': 'data_size',
            'priority': 'medium',
            'message': f"Dataset is relatively small ({n_rows} rows). More data could improve model robustness."
        })
    
    # Feature to sample ratio
    if n_rows / n_cols < 10:
        recommendations.append({
            'type': 'feature_ratio',
            'priority': 'high',
            'message': f"High feature-to-sample ratio ({n_cols} features, {n_rows} samples). Consider feature selection or dimensionality reduction."
        })
    
    # Based on warnings
    warning_types = {w['type'] for w in warnings}
    
    if 'severe_class_imbalance' in warning_types:
        recommendations.append({
            'type': 'imbalance',
            'priority': 'high',
            'message': "Use balanced metrics (F1, ROC-AUC), class weights, or resampling techniques (SMOTE, undersampling)."
        })
    
    if 'high_cardinality' in warning_types:
        recommendations.append({
            'type': 'encoding',
            'priority': 'medium',
            'message': "Consider target encoding, feature hashing, or grouping rare categories for high-cardinality features."
        })
    
    if 'missing_data' in warning_types:
        recommendations.append({
            'type': 'missing_data',
            'priority': 'medium',
            'message': "Address missing data through imputation, dropping columns, or using algorithms that handle missing values."
        })
    
    # Model-specific recommendations
    if target_column:
        # Check if target is numeric (potential regression problem)
        if df[target_column].dtype in ['int64', 'float64'] and df[target_column].nunique() > 20:
            recommendations.append({
                'type': 'problem_type',
                'priority': 'info',
                'message': "Target appears numeric with many unique values. Consider using regression instead of classification."
            })
    
    return recommendations

def get_sample_input_format(file, target_column: Optional[str] = None) -> Dict[str, Any]:
    """Generate sample input format for model testing."""
    try:
        df = pd.read_csv(file)
        file.seek(0)
        
        # Exclude target column from features
        feature_columns = [col for col in df.columns if col != target_column]
        
        # Generate sample input
        sample_input = {}
        for col in feature_columns:
            if df[col].dtype in ['int64', 'float64']:
                # Use median for numeric columns
                sample_input[col] = float(df[col].median()) if not df[col].isnull().all() else 0.0
            else:
                # Use most common value for categorical columns
                mode_value = df[col].mode()
                sample_input[col] = mode_value.iloc[0] if len(mode_value) > 0 else "sample_value"
        
        return {
            'success': True,
            'sample_input': sample_input,
            'feature_columns': feature_columns,
            'data_types': {col: str(df[col].dtype) for col in feature_columns}
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"Error generating sample input: {str(e)}"
        }