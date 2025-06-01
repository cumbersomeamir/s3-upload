#Also accepts .mp3 and .wav now,
import os
import boto3
import pandas as pd
from botocore.exceptions import NoCredentialsError

# Environment variables
AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
AWS_REGION = os.getenv('AWS_REGION')

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

def upload_file_to_s3(file_path, bucket_name, s3_key):
    """Uploads a file to S3 and returns the file URL."""
    try:
        s3_client.upload_file(file_path, bucket_name, s3_key)
        s3_url = f"https://{bucket_name}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
        return s3_url
    except FileNotFoundError:
        print(f"Error: File not found - {file_path}")
    except NoCredentialsError:
        print("Error: AWS credentials not available")
    except Exception as e:
        print(f"Error uploading {file_path}: {e}")
    return None

def process_files(folder_path):
    """Loops through all supported files in a folder and uploads them to S3."""
    s3_urls = []
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            if file_name.lower().endswith((
                '.jpeg', '.jpg', '.png', '.webp', '.mp4',
                '.mp3', '.wav'
            )):
                file_path = os.path.join(root, file_name)
                s3_key = file_name  # Use original file name as the S3 key
                print(f"Uploading {file_name} to S3...")
                s3_url = upload_file_to_s3(file_path, S3_BUCKET_NAME, s3_key)
                if s3_url:
                    print(f"Uploaded: {s3_url}")
                    s3_urls.append({"File Name": file_name, "S3 URL": s3_url})
                else:
                    print(f"Failed to upload {file_name}")
    return s3_urls

def save_to_excel(s3_urls, output_file):
    """Saves the list of S3 URLs to an Excel file."""
    df = pd.DataFrame(s3_urls)
    df.to_excel(output_file, index=False)
    print(f"Saved S3 URLs to {output_file}")

if __name__ == "__main__":
    folder_path = "/Users/amir/Desktop/all_programs/chop/lib/python3.12/site-packages/to-convert"  # Path to the folder containing files
    output_file = "homepage_files.xlsx"  # Output Excel file name
    if os.path.exists(folder_path):
        print("Processing files...")
        s3_urls = process_files(folder_path)
        print("\nAll uploaded files:")
        for entry in s3_urls:
            print(entry["S3 URL"])
        save_to_excel(s3_urls, output_file)
    else:
        print(f"Error: Folder not found - {folder_path}")
