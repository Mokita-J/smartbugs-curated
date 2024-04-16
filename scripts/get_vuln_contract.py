import sys
import re
import json
import os

def get_contract_names_and_lines(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.readlines()
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return []

    contracts = []

    contract_pattern = re.compile(r'^\s*contract\s+(\w+)\b')

    for i, line in enumerate(content, start=1):
        match = contract_pattern.search(line)
        if match:
            contract_name = match.group(1)
            contracts.append((contract_name, i))

    return contracts

def get_contracts_for_lines(file_path, line_numbers):
    contracts = get_contract_names_and_lines(file_path)
    vuln_contracts = set()
    print(contracts)
    for line_number in line_numbers:
        for i in range(len(contracts) -1, -1, -1):
            print(contracts[i])
            if contracts[i][1] < line_number:
                vuln_contracts.add(contracts[i][0])
                break
    return list(vuln_contracts)

def get_vuln_contract_name(file_path):
    vulnerable_lines = []
    with open(file_path, 'r') as file:
        for line in file:
            if '@vulnerable_at_lines' in line:
                vulnerable_lines.extend(map(int, re.findall(r'\d+', line)))

    if vulnerable_lines:
        contract_names = get_contracts_for_lines(file_path, vulnerable_lines)
        if contract_names:
            print(f"The vulnerable lines {vulnerable_lines} are in the contracts: {contract_names}.")
            # Read existing vulnerabilities data
            with open('vulnerabilities.json', 'r') as json_file:
                vulnerabilities_data = json.load(json_file)

            # Update corresponding entries with contract names
            filename = os.path.basename(file_path)
            for vulnerability in vulnerabilities_data:
                if vulnerability['name'] == filename:
                    vulnerability['contract_names'] = contract_names
                    break

            # Write the updated data back to the JSON file
            with open('vulnerabilities.json', 'w') as json_file:
                json.dump(vulnerabilities_data, json_file, indent=4)
        else:
            print("No contracts found containing the vulnerable lines.")
    else:
        print("No vulnerable lines found in the file.")


def process_directory(directory):
    for root, _, files in os.walk(directory):
        for file_name in files:
            if file_name.endswith('.sol'):
                file_path = os.path.join(root, file_name)
                print(f"Processing {file_path}")
                get_vuln_contract_name(file_path)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <directory>")
        sys.exit(1)

    dataset_directory = sys.argv[1]
    if not os.path.isdir(dataset_directory):
        print(f"Directory not found: {dataset_directory}")
        sys.exit(1)

    process_directory(dataset_directory)
    # get_vuln_contract_name(dataset_directory)
