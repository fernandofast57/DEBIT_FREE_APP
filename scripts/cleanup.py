
import os
import shutil

def cleanup():
    """Clean up temporary files and cached data"""
    # Directories to clean
    cleanup_dirs = [
        '__pycache__',
        '.pytest_cache',
        'logs/*.log',
        'instance/*.db*'
    ]
    
    # Clean up directories
    for pattern in cleanup_dirs:
        if '*' in pattern:
            # Handle patterns with wildcards
            dir_path = os.path.dirname(pattern)
            if os.path.exists(dir_path):
                file_pattern = os.path.basename(pattern)
                for file in os.listdir(dir_path):
                    if file.endswith(file_pattern.replace('*', '')):
                        os.remove(os.path.join(dir_path, file))
        else:
            # Handle direct directory removal
            for root, dirs, files in os.walk('.', topdown=False):
                if pattern in dirs:
                    shutil.rmtree(os.path.join(root, pattern))

    print("✅ Cleanup completed successfully")

if __name__ == "__main__":
    cleanup()
