import subprocess
import re
import argparse
import configparser
from datetime import datetime
from pathlib import Path
import os

def run_fscan(fscan_path, target_file, port_range, output_file):
    print("[*] 开始执行 fscan 扫描...")
    cmd = f"{fscan_path} -hf {target_file} -p {port_range} -o {output_file}"
    result = subprocess.run(cmd, shell=True)
    if result.returncode == 0:
        print("[+] fscan 扫描完成。")
        extract_urls_from_fscan(fscan_output, url_list)
    else:
        print("[-] fscan 执行失败。")

def extract_urls_from_fscan(output_file, url_file):
    print("[*] 正在提取 URL...")
    url_pattern = re.compile(r'(https?://[\d\.]+:\d+)')
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
    urls = sorted(set(url_pattern.findall(content)))
    with open(url_file, 'w') as f:
        for url in urls:
            f.write(url + '\n')
    print(f"[+] 提取到 {len(urls)} 个 URL，写入 {url_file}。")
    run_xray(xray_path, url_list, xray_output)

def run_xray(xray_path, url_file, result_file):
    print("[*] 开始执行 xray 扫描...")
    # 获取 xray 所在目录
    xray_dir = Path(xray_path).parent
    # 转换为绝对路径，避免 cwd 影响路径识别
    abs_url_file = str(Path(url_file).resolve())
    abs_result_file = str(Path(result_file).resolve())
    cmd = f"{xray_path} webscan --url-file {abs_url_file} --html-output {abs_result_file}"
    subprocess.run(cmd, shell=True, cwd=xray_dir)
    print("[+] xray 扫描完成，结果保存在:", result_file)

def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    fscan_path = config.get('Paths', 'fscan')
    xray_path = config.get('Paths', 'xray')
    port_range = config.get('Scan', 'port')
    return fscan_path, xray_path, port_range

def get_timestamp():
    now = datetime.now()
    return now.strftime("%m%d_%H%M")  # 月日_小时分钟

def make_output_dir(timestamp):
    folder = timestamp
    if not os.path.exists(folder):
        os.makedirs(folder)
    return folder

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="fscan + xray 自动化扫描")
    parser.add_argument('-f', dest='target_file', required=True, help='包含目标 IP 的文本文件路径')
    args = parser.parse_args()

    fscan_path, xray_path, port_range = load_config()
    timestamp = get_timestamp()
    out_dir = make_output_dir(timestamp)

    fscan_output = os.path.join(out_dir, f"fscan_output_{timestamp}.txt")
    url_list = os.path.join(out_dir, f"urls_{timestamp}.txt")
    xray_output = os.path.join(out_dir, f"xray_output_{timestamp}.html")

    run_fscan(fscan_path, args.target_file, port_range, fscan_output)