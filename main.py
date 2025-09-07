#!/usr/bin/env python3  

import cv2
import numpy as np
import sys
import os
import piexif
import glob

def detect_moon_center(image_path):
    # 画像の読み込み
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read image from {image_path}")
        return None, None, None, None, None

    # Exifデータの読み込み
    exif_dict = None
    try:
        exif_dict = piexif.load(image_path)
    except piexif.InvalidImageDataError:
        print(f"Warning: No valid Exif data found in {image_path}")
    except Exception as e:
        print(f"Error loading Exif data: {e}")

    # グレースケール変換
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # ガウシアンブラーを適用してノイズを軽減
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # ハフ変換による円検出
    # dp: 画像解像度に対する投票空間の解像度の逆数。1は同じ解像度、2は半分の解像度。
    # minDist: 検出される円の中心間の最小距離。
    # param1: Cannyエッジ検出器の2つのしきい値のうち大きい方。
    # param2: 投票数（アキュムレータ値）のしきい値。これが小さいほど多くの偽の円が検出される。
    # minRadius: 最小円半径。
    # maxRadius: 最大円半径。
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
                               param1=100, param2=30, minRadius=50, maxRadius=0) # maxRadius=0は自動設定

    if circles is not None:
        circles = np.uint16(np.around(circles))
        # 検出された円の中から最も確からしい（ここでは最初の）円を選択
        # 複数の円が検出された場合、より洗練された選択ロジックが必要になることがあります。
        # 例: 最も投票数の多い円、最も大きい円など。
        x, y, r = circles[0, 0]
        center = (int(x), int(y))
        radius = int(r)
    else:
        print("No circles found. Please adjust HoughCircles parameters or check the image.")
        return None, None, None, None, None

    # 結果の描画（オプション）
    # 元の画像に中心と円を描画して確認
    output_img_with_annotations = img.copy()
    cv2.circle(output_img_with_annotations, center, radius, (0, 255, 0), 2) # 緑色の円
    cv2.circle(output_img_with_annotations, center, 5, (0, 0, 255), -1)    # 赤色の中心点

    return center, radius, img, output_img_with_annotations, exif_dict

def crop_and_save_centered_image(original_img, center, output_filename_prefix, exif_data, crop_width, crop_height, suffix):
    h, w = original_img.shape[:2]
    cx, cy = center

    # 切り抜き範囲の開始座標を計算
    x_start = cx - crop_width // 2
    y_start = cy - crop_height // 2

    # 画像の境界内に収まるように調整
    # x_startが負の場合、0に調整
    x_start = max(0, x_start)
    # x_start + crop_widthが画像の幅を超える場合、x_startを左にシフト
    x_start = min(x_start, w - crop_width) if w >= crop_width else 0

    # y_startが負の場合、0に調整
    y_start = max(0, y_start)
    # y_start + crop_heightが画像の高さを超える場合、y_startを上にシフト
    y_start = min(y_start, h - crop_height) if h >= crop_height else 0

    # 切り抜き範囲の終了座標を計算
    x_end = x_start + crop_width
    y_end = y_start + crop_height

    # 画像を切り抜き
    cropped_img = original_img[y_start:y_end, x_start:x_end]

    # ファイル名を生成
    base_name = os.path.splitext(output_filename_prefix)[0]
    extension = os.path.splitext(output_filename_prefix)[1]
    output_filename = f"{base_name}{suffix}{extension}"

    # 切り抜いた画像を保存
    cv2.imwrite(output_filename, cropped_img)
    print(f"Cropped image saved as {output_filename}")

    # Exifデータを新しい画像に書き込む
    if exif_data:
        try:
            piexif.insert(piexif.dump(exif_data), output_filename)
            print(f"Exif data copied to {output_filename}")
        except Exception as e:
            print(f"Error copying Exif data: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 moon_center_detector.py <image_path or 'auto'>")
        sys.exit(1)

    arg = sys.argv[1]
    
    if arg == "auto":
        # IMG_*.JPGパターンでファイルを検索し、昇順に並べて最後のファイルを選択
        img_files = glob.glob("IMG_*.JPG")
        if not img_files:
            print("No IMG_*.JPG files found in current directory")
            sys.exit(1)
        img_files.sort()  # 昇順にソート
        image_path = img_files[-1]  # 最後のファイルを選択
        print(f"Auto-selected file: {image_path}")
    else:
        image_path = arg
    center, radius, original_img, output_img_with_annotations, exif_data = detect_moon_center(image_path)

    if center and radius and original_img is not None:
        print(f"Moon Center: {center}")
        print(f"Moon Radius: {radius}")

        # アノテーション付き画像を保存（デバッグ用）
        output_annotated_filename = "detected_moon_" + os.path.basename(image_path)
        cv2.imwrite(output_annotated_filename, output_img_with_annotations)
        print(f"Annotated image saved as {output_annotated_filename}")

        # 1000x1000 画像を 'a' サフィックスで保存
        crop_and_save_centered_image(original_img, center, os.path.basename(image_path), exif_data, 1000, 1000, "a")

        # 1920x1080 画像を 'b' サフィックスで保存
        crop_and_save_centered_image(original_img, center, os.path.basename(image_path), exif_data, 1920, 1080, "b")

        # 1080x1920 画像を 'c' サフィックスで保存
        crop_and_save_centered_image(original_img, center, os.path.basename(image_path), exif_data, 1080, 1920, "c")
    else:
        print("Failed to detect moon center or process image.")
