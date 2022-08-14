import requests
import json
import os

# PI API https://pi.delivery/#apipi_get

def get_digits(start: int=0, n_digits: int=100):
    # Request server for Pi digits
    req = requests.get("https://api.pi.delivery/v1/pi", params = [("start", start), ("numberOfDigits", n_digits)])
    if req.status_code != 200:
        print(f">>> GET REQUEST ERROR: '{req.text}'")
        return
    
    # Extract digits from response json
    req_dic = json.loads(req.text)
    digits = req_dic["content"]
    return digits

def get_starting_point(path, file_len_limit):
    # Get all current files
    files = os.listdir(path)
    txt_files = [file for file in files if ".txt" in file]
    if len(txt_files) == 0:
        return "0.txt", 0, 0
    
    # Get the last file
    txt_files.sort()
    last_file = txt_files[-1]
    file_n = int( last_file.split(".")[0] )

    # Get current number of digits
    number_digits = 0
    with open(last_file, "r") as f:
        number_digits = len(f.read())
    total_digits = file_n * file_len_limit + number_digits

    # Create new file if maxed out
    if number_digits >= file_len_limit:
        if number_digits > file_len_limit:
            print(f"/!\\ WARNING: last file '{last_file}' size ({number_digits}) exceeds max of {file_len_limit}")
        return f"{file_n + 1}.txt", total_digits, 0

    overflow = number_digits

    return last_file, total_digits, overflow

def main():
    file_len_limit = 100#100_000_000
    # files_path = "."
    files_path = "./pi_files"
    cur_file_name, cur_decimal, overflow = get_starting_point(files_path, file_len_limit)
    print(cur_file_name, cur_decimal, overflow)

    digits_per_request = 10#1000
    cur_digits = ""
    timeout_timer = file_len_limit / digits_per_request + 100
    cur_file_len = overflow

    i=0 
    while cur_file_len < file_len_limit and timeout_timer > 0:
        cur_req_number_of_digits = digits_per_request - overflow
        cur_digits = get_digits(cur_decimal, cur_req_number_of_digits)

        with open(cur_file_name, "a") as cur_file:
            for digit in cur_digits:
                cur_file.write(digit)
                cur_file_len += 1
                cur_decimal += 1
                # print(cur_file_len)
        
        overflow = max(0, (cur_file_len + digits_per_request) - file_len_limit )
        timeout_timer -= 1
        i+=1
    # os.system(f"cd {path} && git push") <<< TODO

    print()

if __name__ == "__main__":
    main()