"""Simple CNN templates for image tasks (Keras).

Provides `get_model(input_shape, num_classes, config=None)` returning a compiled model.
"""
try:
    from utils.lazy_tf import tf, is_available as tf_is_available
    HAS_DEPS = tf_is_available()
except Exception:
    keras = None


def get_model(input_shape, num_classes=1, config=None):
    if keras is None:
        raise RuntimeError("TensorFlow not installed")
    cfg = config or {}
    filters = cfg.get('filters', [32, 64])
    kernel_size = cfg.get('kernel_size', 3)
    pool_size = cfg.get('pool_size', 2)
    dropout = cfg.get('dropout', 0.25)
    final_activation = cfg.get('final_activation', None)
    optimizer = cfg.get('optimizer', 'adam')
    loss = cfg.get('loss', 'sparse_categorical_crossentropy' if num_classes>1 else 'binary_crossentropy')
    metrics = cfg.get('metrics', ['accuracy'])

    inputs = keras.layers.Input(shape=input_shape)
    x = inputs
    for f in filters:
        x = keras.layers.Conv2D(f, kernel_size, activation='relu', padding='same')(x)
        x = keras.layers.MaxPooling2D(pool_size)(x)
    x = keras.layers.Flatten()(x)
    if dropout and dropout>0:
        x = keras.layers.Dropout(dropout)(x)
    outputs = keras.layers.Dense(num_classes if num_classes>1 else 1, activation=final_activation)(x)

    model = keras.Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer=optimizer, loss=loss, metrics=metrics)
    return model
