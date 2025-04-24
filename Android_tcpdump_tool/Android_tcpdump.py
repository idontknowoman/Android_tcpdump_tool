import argparse
import os
import subprocess


# 在命令行的返回结果中解析需要查找的attr值
def parse_result(result, attr):
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None
    # 解析命令行返回结果
    lines = result.stdout.splitlines()
    for line in lines:
        if attr in line:
            # 提取attr_value
            attr_value = line.split(attr)[1]
            if "'" in attr_value:
                attr_value = attr_value.split("'")[1]
            elif '"' in attr_value:
                attr_value = attr_value.split('"')[1]
            return attr_value
    return None


# 获取目标应用的package_name
def get_package_name(apk_file_path):
    # 使用aapt命令获取apk的包名
    cmd = f"aapt dump badging {apk_file_path}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return parse_result(result, "name=")


# 获取目标应用的userID
def get_userID(package_name):
    cmd = f"adb shell su -c 'cat /data/system/packages.xml | grep {package_name}'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return parse_result(result, "userId=")


def edit_iptables(userId):
    # 把OUTPUT数据包里面，用户ID是10012的流打上10012的流标签
    cmd = f"adb shell su -c 'iptables -A OUTPUT -m owner --uid-owner {userId} -j CONNMARK --set-mark {userId}'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    # 把入站流中带有10012标签的数据包放到nflog消息池中，消息池的标号为10012
    cmd = f"adb shell su -c 'iptables -A INPUT -m connmark --mark {userId} -j NFLOG --nflog-group {userId}'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    # 把出站流中带有10012标签的数据包放到nflog消息池中，消息池的标号为10012
    cmd = f"adb shell su -c 'iptables -A OUTPUT -m connmark --mark {userId} -j NFLOG --nflog-group {userId}'"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    return True


# 获取目标应用的流量
def get_traffic(userId, timeout=300):
    # 使用tcpdump命令获取流量
    cmd = f"adb shell su -c 'tcpdump -i nflog:{userId} -w /sdcard/{userId}.pcap'"
    # 执行命令，并设定超时时间为300秒，给5分钟的时间触发应用行为，记录这段时间内的流量数据
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        print(f"Timeout: {timeout} seconds")
        # 超时后停止tcpdump
        stop_cmd = f"adb shell su -c 'killall tcpdump'"
        subprocess.run(stop_cmd, shell=True, capture_output=True, text=True)
        return True
    return False


def save_pcap(userId, output_path=None):
    if output_path is None:
        # 如果没有指定输出路径，则默认保存到当前目录
        output_path = os.getcwd()
    if os.path.isdir(output_path):
        # 如果输出路径是目录，则将文件保存到该目录
        output_file = os.path.join(output_path, f"{userId}.pcap")
    else:
        output_file = output_path
    cmd = f"adb pull /sdcard/{userId}.pcap {output_file}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    return True


def main():
    # 使用 argparse 定义命令行参数
    parser = argparse.ArgumentParser(description="Android 应用抓包工具")
    parser.add_argument("-a", "--apk", help="目标应用的 APK 文件路径", required=False)
    parser.add_argument("-t", "--timeout", type=int, help="抓包超时时间（秒）")
    parser.add_argument("-o", "--output", help="抓包结果文件保存路径")

    args = parser.parse_args()

    # 获取包名
    if args.apk:
        package_name = get_package_name(args.apk)
        if not package_name:
            print("无法从 APK 文件中获取包名")
            return

    if not args.apk:
        print("请提供应用 APK 文件路径")
        return

    print(f"目标应用包名: {package_name}")

    # 获取 userId
    userId = get_userID(package_name)
    if not userId:
        print("无法获取目标应用的 userId")
        return

    print(f"目标应用 userId: {userId}")

    # 配置 iptables
    if not edit_iptables(userId):
        print("配置 iptables 失败")
        return

    # 开始抓包
    print(f"开始抓包，超时时间为 {args.timeout} 秒...")
    if get_traffic(userId, timeout=args.timeout):
        print(f"抓包完成，数据已保存到 /sdcard/{userId}.pcap")
    else:
        print("抓包失败")
        return
    
    # 保存抓取到的流量包文件
    if save_pcap(userId, output_path=args.output):
        if not args.output:
            print(f"{userId}.pcap已保存到当前目录")
        else:
            print(f"{userId}.pcap已保存到{args.output}")
    else:
        print("pcap文件拉取失败")
        return


if __name__ == "__main__":
    main()
