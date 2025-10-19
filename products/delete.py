import os
import glob

for root, dirs, files in os.walk('.'):
    if 'migrations' in dirs:
        migration_dir = os.path.join(root, 'migrations')
        py_files = glob.glob(os.path.join(migration_dir, '*.py'))
        pyc_files = glob.glob(os.path.join(migration_dir, '*.pyc'))

        for file in py_files + pyc_files:
            if not file.endswith('__init__.py'):
                print(f'Deleting: {file}')
                os.remove(file)
