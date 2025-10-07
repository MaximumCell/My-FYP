// Add all possible model types for static export
export function generateStaticParams() {
    return [
        { modelType: 'regression' },
        { modelType: 'classification' },
    ];
}