"""Simple MLP model definition using Keras (TensorFlow).

Naming convention: file names and exported functions should mirror previous model conventions
(e.g., train_model, test_model naming used in existing regression/classifier modules).
"""

try:
    from utils.lazy_tf import tf, is_available as tf_is_available
    HAS_DEPS = tf_is_available()
    import numpy as np
except Exception:
    keras = None
    np = None


def build_model(input_shape, output_units=1, config=None):
    """Build a configurable MLP.

    config keys (all optional):
      - hidden_units: list of ints, e.g. [128, 64]
      - activations: single activation or list matching hidden_units
      - dropout: float (applied after each hidden layer)
      - final_activation: activation for output layer (None for linear)
      - optimizer: optimizer string or keras optimizer
      - loss: loss name
      - metrics: list of metrics

    This keeps backward compatibility while allowing flexible architectures.
    """
    if keras is None:
        raise RuntimeError("TensorFlow not installed")

    cfg = config or {}
    hidden_units = cfg.get('hidden_units', [128, 64])
    activations = cfg.get('activations', 'relu')
    dropout = cfg.get('dropout', 0.0)
    final_activation = cfg.get('final_activation', None)
    optimizer = cfg.get('optimizer', 'adam')
    loss = cfg.get('loss', 'mse')
    metrics = cfg.get('metrics', ['mae'])

    if isinstance(activations, str):
        activations = [activations] * len(hidden_units)

    inputs = keras.layers.Input(shape=input_shape)
    x = inputs
    for i, units in enumerate(hidden_units):
        act = activations[i] if i < len(activations) else activations[-1]
        x = keras.layers.Dense(units, activation=act)(x)
        if dropout and dropout > 0:
            x = keras.layers.Dropout(dropout)(x)

    outputs = keras.layers.Dense(output_units, activation=final_activation)(x)
    model = keras.Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer=optimizer, loss=loss, metrics=metrics)
    return model


# Backwards-compatible function name used by other scripts
def get_model(input_shape, output_units=1, config=None):
    return build_model(input_shape, output_units, config=config)
