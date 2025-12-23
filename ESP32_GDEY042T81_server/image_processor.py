import os
import uuid
from PIL import Image, ImageOps
from typing import Tuple, Optional
from config import settings

class ImageProcessor:
    def __init__(self):
        self.width = settings.ink_width
        self.height = settings.ink_height
        self.upload_dir = settings.upload_dir
        self.processed_dir = settings.processed_dir
        
        # 确保目录存在
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
    
    def process_image(self, image_path: str, grayscale: bool = True, dither: bool = True) -> str:
        """
        处理上传的图片，使其适配墨水屏显示
        
        Args:
            image_path: 原始图片路径
            grayscale: 是否转换为灰度图
            dither: 是否使用抖动算法
            
        Returns:
            处理后图片的相对路径
        """
        try:
            # 打开原始图片
            img = Image.open(image_path)
            
            # 转换为RGB模式（处理RGBA等格式）
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # 自动旋转（基于EXIF信息）
            img = ImageOps.exif_transpose(img)
            
            # 计算缩放比例，保持宽高比
            img_ratio = img.width / img.height
            target_ratio = self.width / self.height
            
            if img_ratio > target_ratio:
                # 图片较宽，以高度为准
                new_height = self.height
                new_width = int(self.height * img_ratio)
            else:
                # 图片较高，以宽度为准
                new_width = self.width
                new_height = int(self.width / img_ratio)
            
            # 缩放图片
            img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # 居中裁剪到目标尺寸
            left = (new_width - self.width) // 2
            top = (new_height - self.height) // 2
            right = left + self.width
            bottom = top + self.height
            img = img.crop((left, top, right, bottom))
            
            # 转换为灰度图
            if grayscale:
                img = img.convert('L')
            
            # 生成处理后的文件名
            filename = f"{uuid.uuid4()}.bmp"
            processed_path = os.path.join(self.processed_dir, filename)
            
            # 保存为BMP格式（墨水屏易解析）
            if grayscale:
                # 黑白图片，使用抖动算法
                if dither:
                    img.convert('1').save(processed_path)
                else:
                    img.convert('1', dither=Image.NONE).save(processed_path)
            else:
                # 彩色图片，转换为RGB模式
                img.save(processed_path)
            
            # 返回相对路径
            return os.path.relpath(processed_path)
            
        except Exception as e:
            raise Exception(f"图片处理失败: {str(e)}")
    
    def save_upload(self, file_data: bytes, filename: str) -> str:
        """
        保存上传的原始文件
        
        Args:
            file_data: 文件二进制数据
            filename: 原始文件名
            
        Returns:
            保存后的文件路径
        """
        # 生成唯一文件名
        file_ext = os.path.splitext(filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        upload_path = os.path.join(self.upload_dir, unique_filename)
        
        # 保存文件
        with open(upload_path, "wb") as f:
            f.write(file_data)
        
        return upload_path
    
    def get_image_info(self, image_path: str) -> dict:
        """
        获取图片信息
        
        Args:
            image_path: 图片路径
            
        Returns:
            图片信息字典
        """
        try:
            with Image.open(image_path) as img:
                return {
                    "width": img.width,
                    "height": img.height,
                    "mode": img.mode,
                    "format": img.format,
                    "size_bytes": os.path.getsize(image_path)
                }
        except Exception as e:
            raise Exception(f"获取图片信息失败: {str(e)}")

# 全局图片处理器实例
image_processor = ImageProcessor()