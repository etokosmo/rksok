import os


base_dir = os.path.dirname(__file__) or '.'
path_to_db = os.path.join(base_dir, 'models', 'notebook.db')
path_to_logs = os.path.join(base_dir, 'logs', 'logs.log')
