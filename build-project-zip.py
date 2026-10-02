import os
import zipfile

def make_zip():
    output_path = os.path.join('public', 'lost_god_fullstack.zip')
    ignore_dirs = {
        'node_modules', '.git', '.aistudio', 'dist', '__pycache__', '.vite'
    }
    ignore_files = {
        'lost_god_fullstack.zip', 'test.txt'
    }
    keep_dotfiles = {'.dockerignore', '.gitignore'}

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('.'):
            # Prune ignored directories
            dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]
            
            for file in files:
                if file in ignore_files or file.endswith('.pyc'):
                    continue
                if file.startswith('.') and file not in keep_dotfiles:
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, '.')
                zipf.write(file_path, arcname)
                
    print(f"Created {output_path} ({os.path.getsize(output_path)} bytes)")

if __name__ == '__main__':
    make_zip()
