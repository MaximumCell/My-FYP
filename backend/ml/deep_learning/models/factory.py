"""Model factory to create models by name with a config dict.

Usage:
  from deep_learning.models.factory import get_model_by_name
  model = get_model_by_name('mlp', input_shape=(32,), output_units=1, config={...})
"""
try:
    from .simple_mlp import get_model as mlp_get
    from .cnn import get_model as cnn_get
    from .sequence import get_model as seq_get
    from .transformer import get_model as trf_get
except Exception:
    # Import errors will be surfaced when calling functions if TF missing
    mlp_get = None
    cnn_get = None
    seq_get = None
    trf_get = None


def get_model_by_name(name, input_shape, output_units=1, config=None):
    name = name.lower()
    if name in ('mlp', 'dense', 'simple_mlp'):
        if mlp_get is None:
            raise RuntimeError('MLP model unavailable (check TensorFlow install)')
        return mlp_get(input_shape, output_units, config)
    if name in ('cnn', 'conv', 'convnet'):
        if cnn_get is None:
            raise RuntimeError('CNN model unavailable (check TensorFlow install)')
        return cnn_get(input_shape, output_units, config)
    if name in ('sequence', 'rnn', 'lstm', 'gru'):
        if seq_get is None:
            raise RuntimeError('Sequence model unavailable (check TensorFlow install)')
        return seq_get(input_shape, output_units, config)
    if name in ('transformer', 'trf'):
        if trf_get is None:
            raise RuntimeError('Transformer model unavailable (check TensorFlow install)')
        return trf_get(input_shape, output_units, config)
    raise ValueError(f'Unknown model name: {name}')
