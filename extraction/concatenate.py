import os
import sys

def concatenate_jsonl_files(directory_path, output_file_path):
    with open(output_file_path, 'w') as output_file:
        for root, dirs, files in os.walk(directory_path):
            for filename in files:
                if filename.endswith('.jsonl'):
                    file_path = os.path.join(root, filename)
                    with open(file_path, 'r') as input_file:
                        output_file.write(input_file.read())

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python script.py directory_path output_file_path")
    else:
        directory_path = sys.argv[1]
        output_file_path = sys.argv[2]
        concatenate_jsonl_files(directory_path, output_file_path)
