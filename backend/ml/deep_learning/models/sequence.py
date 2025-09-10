"""Sequence models (LSTM/GRU) templates for time-series and text.

Provides `get_model(input_shape, output_units=1, config=None)`.
"""
try:
    from tensorflow import keras
except Exception:
    keras = None


def get_model(input_shape, output_units=1, config=None):
    if keras is None:
        raise RuntimeError("TensorFlow not installed")
    cfg = config or {}
    rnn_type = cfg.get('rnn_type', 'lstm')
    rnn_units = cfg.get('rnn_units', 64)
    return_sequences = cfg.get('return_sequences', False)
    dropout = cfg.get('dropout', 0.2)
    final_activation = cfg.get('final_activation', None)
    optimizer = cfg.get('optimizer', 'adam')
    loss = cfg.get('loss', 'mse')
    metrics = cfg.get('metrics', ['mae'])

    inputs = keras.layers.Input(shape=input_shape)
    if rnn_type.lower() == 'gru':
        x = keras.layers.GRU(rnn_units, return_sequences=return_sequences)(inputs)
    else:
        x = keras.layers.LSTM(rnn_units, return_sequences=return_sequences)(inputs)
    if dropout and dropout>0:
        x = keras.layers.Dropout(dropout)(x)
    outputs = keras.layers.Dense(output_units, activation=final_activation)(x)

    model = keras.Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer=optimizer, loss=loss, metrics=metrics)
    return model
