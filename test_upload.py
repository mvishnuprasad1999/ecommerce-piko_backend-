import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name="drp2l34jj",
    api_key="555413531481499",
    api_secret="1RWW906VATQMLtUM2zAptXcklK4"
)

result = cloudinary.uploader.upload("images/milk_milma_pack.png")

print("UPLOAD SUCCESS:", result["secure_url"])