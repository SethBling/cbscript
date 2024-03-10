import cbscript
import sys
import time
import source_file
import scriptparse
import os
import glob
from tqdm import tqdm
import matplotlib.pyplot as plt

def compile_cbscript(file_path):
    original_directory = os.getcwd()
    source = source_file.source_file(file_path)
    script_directory = source.get_directory()
    os.chdir(script_directory)
    script = cbscript.cbscript(source, scriptparse.parse)
    script.try_to_compile()
    os.chdir(original_directory) 

def run_test_harness(directory, iterations=20):
    cbscript_files = glob.glob(os.path.join(directory, '*.cbscript'))

    compile_times = {file: 0 for file in cbscript_files}

    for file in tqdm(cbscript_files, desc="Compiling .cbscript files"):
        tqdm.write(f"{file=}")
        with tqdm(total=iterations, desc=f"Compiling: {os.path.basename(file)}", leave=False) as pbar:
            for _ in range(iterations):
                start_time = time.time()
                compile_cbscript(file)
                end_time = time.time()
                compile_times[file] += (end_time - start_time)
                pbar.update(1)
    
        average_times = {file: total_time / iterations for file, total_time in compile_times.items()}

    sorted_files = sorted(average_times.items(), key=lambda x: x[1])

    file_names = [os.path.basename(file) for file, _ in sorted_files]
    times = [time for _, time in sorted_files]

    plt.figure(figsize=(10, len(file_names) * 0.5))
    plt.barh(file_names, times, color='skyblue')
    plt.xlabel('Average Compile Time (seconds)')
    plt.title('Average Compile Time of .cbscript Files')
    plt.show()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("You must include the directory path containing .cbscript files.")
        exit()

    directory = sys.argv[1]
    run_test_harness(directory)