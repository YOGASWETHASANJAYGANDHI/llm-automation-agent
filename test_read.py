file_path = r"C:\data\dates.txt"

try:
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
        print("File content:\n", content)
except Exception as e:
    print("Error reading file:", e)
