#!/bin/bash

echo "===================================================="
echo "  Claude Prompt Logger Installer for macOS/Linux"
echo "===================================================="
echo

# Kiểm tra Python
if ! command -v python3 &> /dev/null
then
    echo "[ERROR] Python3 chưa được cài đặt hoặc chưa được thêm vào PATH."
    echo "Vui lòng cài đặt Python3 và thử lại."
    exit 1
fi

# Hỏi nhập Email (hoặc ấn Enter để lấy mặc định trong file JSON)
read -p "Nhập email của bạn (Ấn Enter để sử dụng cấu hình mặc định trong JSON): " EMAIL

echo
echo "[1/2] Đang tiến hành cài đặt hook..."
if [ -z "$EMAIL" ]; then
    python3 install_hook.py
else
    python3 install_hook.py --employee-email "$EMAIL"
fi

if [ $? -ne 0 ]; then
    echo "[ERROR] Cài đặt thất bại!"
    exit 1
fi

echo
echo "[2/2] Đang chạy kiểm tra kết nối tới Backend (Test)..."
python3 install_hook.py --test

if [ $? -ne 0 ]; then
    echo "[WARNING] Kiểm tra kết nối thất bại! Vui lòng kiểm tra lại ngrok hoặc server backend."
else
    echo "[SUCCESS] Kiểm tra kết nối thành công! Hệ thống đã sẵn sàng."
fi

echo
echo "===================================================="
read -p "Nhấn Enter để thoát..."
