import os

dirs = [
    'docs',
    'docs/images',
    'tests',
    'tests/unit',
    'tests/integration'
]

for dir_path in dirs:
    os.makedirs(dir_path, exist_ok=True)
    print(f"Created directory: {dir_path}")
