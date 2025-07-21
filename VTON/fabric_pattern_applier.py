import cv2
import numpy as np

def load_images(shirt_path, pattern_path, mask_path):
    """Load shirt image, fabric pattern, and binary mask."""
    shirt = cv2.imread(r"C:\Users\namja\Downloads\vton_project\Texture-Reformer\data\cloth\00005_00.jpg")
    pattern = cv2.imread(r"C:\Users\namja\Downloads\vton_project\Texture-Reformer\styles\Fabric077_1K-JPG_Color.jpg")
    mask = cv2.imread(r"C:\Users\namja\Downloads\vton_project\Texture-Reformer\data\cloth-mask\00005_00.jpg", cv2.IMREAD_GRAYSCALE)
    
    if shirt is None or pattern is None or mask is None:
        raise ValueError("Could not load one or more input images.")
    
    return shirt, pattern, mask

def resize_pattern(pattern, target_shape):
    """Resize pattern to match shirt dimensions."""
    return cv2.resize(pattern, (target_shape[1], target_shape[0]), interpolation=cv2.INTER_CUBIC)

def apply_pattern_to_mask(shirt, pattern, mask):
    """Apply pattern to shirt while preserving folds and lighting, with normalization and blending."""
    # Ensure mask is binary
    mask_bin = (mask > 127).astype(np.uint8) * 255

    # Convert shirt to grayscale for luminance
    shirt_gray = cv2.cvtColor(shirt, cv2.COLOR_BGR2GRAY)
    shirt_gray_3c = cv2.cvtColor(shirt_gray, cv2.COLOR_GRAY2BGR)

    # Normalize luminance so the brightest part is 1.0
    luminance = shirt_gray_3c.astype(np.float32)
    luminance = luminance / (luminance.max() + 1e-5)

    # Prepare pattern (float32, [0,1])
    pattern_float = pattern.astype(np.float32) / 255.0

    # Multiply pattern by normalized luminance
    patterned = pattern_float * luminance

    # Blend with original pattern to keep color vivid
    alpha = 0.7  # pattern strength (0.5-0.8 is typical)
    patterned = patterned * alpha + pattern_float * (1 - alpha)

    # Convert back to uint8
    patterned_uint8 = np.clip(patterned * 255, 0, 255).astype(np.uint8)

    # Blend: patterned region where mask is white, original shirt elsewhere
    mask_3c = cv2.merge([mask_bin]*3)
    inv_mask_3c = cv2.bitwise_not(mask_3c)
    shirt_bg = cv2.bitwise_and(shirt, inv_mask_3c)
    shirt_fg = cv2.bitwise_and(patterned_uint8, mask_3c)
    result = cv2.add(shirt_bg, shirt_fg)
    
    return result

def main():
    """Main function to process the images."""
    shirt_path = "shirt.jpg"
    pattern_path = "pattern.jpg"
    mask_path = "mask.png"
    output_path = "patterned_shirt.jpg"

    print("Loading images...")
    shirt, pattern, mask = load_images(shirt_path, pattern_path, mask_path)
    
    print("Resizing pattern...")
    pattern_resized = resize_pattern(pattern, shirt.shape)
    
    print("Applying pattern to shirt...")
    result = apply_pattern_to_mask(shirt, pattern_resized, mask)
    
    print("Saving result...")
    cv2.imwrite(output_path, result)
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    main() 