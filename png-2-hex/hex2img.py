import sys
import os
import re
from PIL import Image
import io

def decode_hex_to_image(input_text_file, output_image_path="decoded_image.jpg"):
    """
    Reads a text file containing C# style hex bytes (0xff, 0x1a...)
    and converts it back to an image.
    """
    if not os.path.exists(input_text_file):
        print(f"Error: File not found at '{input_text_file}'")
        return

    try:
        with open(input_text_file, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # Use regex to find all hex patterns like 0xFF, 0x1b, etc.
    # This ignores spaces, newlines, C# code, braces, etc.
    hex_strings = re.findall(r'0x[0-9a-fA-F]{2}', content)
    
    if not hex_strings:
        print("Error: No hex values (0x..) found in the file.")
        return

    print(f"Found {len(hex_strings)} bytes.")

    try:
        # Convert hex strings to integers, then to a byte array
        byte_data = bytearray([int(h, 16) for h in hex_strings])
        
        # Ensure output path is in current working directory if relative
        if not os.path.isabs(output_image_path):
            output_image_path = os.path.join(os.getcwd(), output_image_path)
        
        # Write to file
        with open(output_image_path, 'wb') as out_f:
            out_f.write(byte_data)
            
        print(f"Successfully saved image to: {output_image_path}")
        
        # Attempt to open/display the image using Pillow
        try:
            image = Image.open(io.BytesIO(byte_data))
            image.show()
            print("Displaying image...")
        except Exception as img_e:
            print(f"Warning: Could not display image automatically. (Is it a valid image format?)\nError: {img_e}")

    except Exception as e:
        print(f"Error converting data: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python hex2img.py <file_with_hex_data.txt> [optional_output_filename]")
        print("Example: python hex2img.py my_hex_dump.txt output.png")
    else:
        in_file = sys.argv[1]
        out_file = sys.argv[2] if len(sys.argv) > 2 else "decoded_image.jpg"
        decode_hex_to_image(in_file, out_file)