# from PIL import Image
#
# from PIL import Image
# import PIL
#
# # Load the image of the plane (make sure the plane is pointing north)
# image = Image.open("./assets/plane_red.png")
#
# # Get the size of the original image
# original_size = image.size  # This returns (width, height)
# print(f"Original image size: {original_size}")
#
# # Define the desired size for all images (you can choose to keep the original size or set a fixed size)
# # For example, to maintain the original size, use:
# size = original_size  # Keep the original size
#
# # Loop over 360 degrees
# for angle in range(361):
#     # Rotate the image by 'angle' degrees
#     rotated_image = image.rotate(-angle, expand=True)
#
#     # Resize the image to the defined size
#     resized_image = rotated_image.resize(size)
#
#     # Save the image as 'angle.png'
#     resized_image.save(f"./assets/plane_red/{angle}.png")
#

from PIL import Image

# Load the image of the plane (make sure the plane is pointing north)
image = Image.open("./assets/plane_blue.png")

# Get the size of the original image
original_size = image.size  # This returns (width, height)
print(f"Original image size: {original_size}")

# Define the desired size for all images (you can choose to keep the original size or set a fixed size)
# For example, to maintain the original size, use:
size = original_size  # Keep the original size

# Loop over 360 degrees
for angle in range(361):
    # Rotate the image by 'angle' degrees
    rotated_image = image.rotate(-angle, expand=True)

    # Resize the image to the defined size
    resized_image = rotated_image.resize(size)

    # Save the image as 'angle.png'
    resized_image.save(f"./assets/plane_blue/{angle}.png")
