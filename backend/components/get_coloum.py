import pandas as pd
from io import StringIO

def get_coloum(file):
    """Reads a file object and returns a list of its column names."""
    try:
        file_content = StringIO(file.stream.read().decode("UTF8"))
        df = pd.read_csv(file_content)
        column_names = df.columns.tolist()
        return column_names
    except Exception as e:
        return {"error": f"Error processing file: {e}"}

# Example usage in a Flask endpoint (commented out):
# @app.route('/get_columns', methods=['POST'])
# def get_columns_route():
#     if 'file' not in request.files:
#         return jsonify({"error": "No file part"}), 400
#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({"error": "No selected file"}), 400
#     if file:
#         column_names = get_coloum(file)
#         if "error" in column_names:
#             return jsonify(column_names), 500
#         else:
#             return jsonify({"columns": column_names}), 200
