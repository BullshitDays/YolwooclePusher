import requests
import json
import os
from tqdm import tqdm 

# PI API https://pi.delivery/#apipi_get

def get_file_size(path):
    if not os.path.exists(path):
        return 0
    with open(path, "r") as f:
        return len(f.read())


def get_digits(start: int=0, n_digits: int=100):
    # Request server for Pi digits
    req = requests.get("https://api.pi.delivery/v1/pi", params = [("start", start), ("numberOfDigits", n_digits)])
    if req.status_code != 200:
        print(f">>> GET REQUEST ERROR: '{req.text}'")
        return
    
    # Extract digits from response json
    digits = list(req.json()["content"])
    return digits

def get_starting_point(path, file_len_limit):
    # Get all current files
    files = os.listdir(path)
    txt_files = [file for file in files if ".txt" in file]
    if len(txt_files) == 0:
        return "0.txt", 0, 0, 0
    
    # Get the last file
    txt_files.sort()
    last_file = txt_files[-1]
    file_n = int( last_file.split(".")[0] )

    # Get current number of digits
    number_digits = 0
    with open(f"{path}/{last_file}", "r") as f:
        number_digits = len(f.read())
    total_digits = file_n * file_len_limit + number_digits

    # Create new file if maxed out
    if number_digits >= file_len_limit:
        if number_digits > file_len_limit:
            print(f"/!\\ WARNING: last file '{last_file}' size ({number_digits}) exceeds max of {file_len_limit}")
        return f"{file_n + 1}.txt", total_digits, 0, file_n+1

    overflow = number_digits

    return last_file, total_digits, overflow, file_n

def main():
    file_len_limit = 1000#100_000_000
    files_path = "./pi_files"
    cur_file_name, cur_decimal, overflow, file_n = get_starting_point(files_path, file_len_limit)
    cur_file_path = f"{files_path}/{cur_file_name}"
    print(cur_file_name, cur_decimal, overflow)

    digits_per_request = 1000
    cur_digits = ""
    cur_file_len = get_file_size(cur_file_path) #overflow

    i=0 
    while True:
        with tqdm(total=file_len_limit) as pbar:
            with open(cur_file_path, "a") as cur_file:
                cur_digits = get_digits(cur_decimal, digits_per_request)

                while cur_file_len < file_len_limit:
                    cur_file.write(cur_digits.pop(0))

                    pbar.update(1)
                    cur_file_len += 1
                    cur_decimal += 1

                    if len(cur_digits) == 0:
                        cur_digits = get_digits(cur_decimal, digits_per_request)
                    # print(cur_file_len)
        
        cur_file_len = 0
        file_n += 1
        cur_file_path = f"{files_path}/{file_n}.txt"
    # os.system(f"cd {path} && git push") <<< TODO

    print()

if __name__ == "__main__":
    main()