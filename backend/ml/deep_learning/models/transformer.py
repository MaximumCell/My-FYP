"""Small transformer encoder template for sequence tasks (Keras).

Provides `get_model(input_shape, output_units=1, config=None)`.
"""
from utils.lazy_tf import tf, is_available as tf_is_available

HAS_DEPS = tf_is_available()


def _get_layers():
    if not HAS_DEPS:
        raise ImportError("TensorFlow not available")
    return tf.keras.layers


def _get_keras():
    if not HAS_DEPS:
        raise ImportError("TensorFlow not available")
    return tf.keras


def get_model(input_shape, output_units=1, config=None):
    """Build a small transformer encoder model lazily using the TF proxy."""
    if not HAS_DEPS:
        raise RuntimeError("TensorFlow not installed")

    layers = _get_layers()
    keras = _get_keras()

    cfg = config or {}
    d_model = cfg.get('d_model', 64)
    num_heads = cfg.get('num_heads', 4)
    ff_dim = cfg.get('ff_dim', 128)
    num_blocks = cfg.get('num_blocks', 1)
    dropout = cfg.get('dropout', 0.1)
    final_activation = cfg.get('final_activation', None)
    optimizer = cfg.get('optimizer', 'adam')
    loss = cfg.get('loss', 'mse')
    metrics = cfg.get('metrics', ['mae'])

    inputs = layers.Input(shape=input_shape)
    x = inputs
    # basic dense projection if input dims differ
    if input_shape[-1] != d_model:
        x = layers.Dense(d_model)(x)

    for _ in range(num_blocks):
        attn_output = layers.MultiHeadAttention(num_heads=num_heads, key_dim=d_model)(x, x)
        attn_output = layers.Dropout(dropout)(attn_output)
        x = layers.LayerNormalization(epsilon=1e-6)(x + attn_output)
        ff = layers.Dense(ff_dim, activation='relu')(x)
        ff = layers.Dense(d_model)(ff)
        ff = layers.Dropout(dropout)(ff)
        x = layers.LayerNormalization(epsilon=1e-6)(x + ff)

    # Pool across time for final output
    x = layers.GlobalAveragePooling1D()(x)
    outputs = layers.Dense(output_units, activation=final_activation)(x)
    model = keras.Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer=optimizer, loss=loss, metrics=metrics)
    return model

