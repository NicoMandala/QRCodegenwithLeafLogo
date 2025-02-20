import streamlit as st
import qrcode
from PIL import Image, ImageDraw, ImageFont
import io
from datetime import datetime

def create_qr_base(url, fill_color="#A7E163", back_color="white"):
    """Create the base QR code with specified colors."""
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=2  # Reduced border for cleaner look
    )
    qr.add_data(url)
    qr.make(fit=True)
    return qr.make_image(fill_color=fill_color, back_color=back_color).convert('RGBA')

def prepare_logo(logo_image, qr_size, scale=0.15):
    """Resize the logo while preserving aspect ratio."""
    logo = logo_image.convert('RGBA')
    # Calculate new width based on QR size while maintaining aspect ratio
    new_width = int(qr_size[0] * scale)
    width_percent = (new_width / float(logo.size[0]))
    new_height = int(float(logo.size[1]) * width_percent)
    return logo.resize((new_width, new_height), Image.Resampling.LANCZOS)

def generate_custom_qr_code(url, custom_text):
    """Generate a custom QR code with logo and styling."""
    # Create base QR code
    qr_image = create_qr_base(url)
    
    # Load the logo from file
    try:
        logo_image = Image.open("logo.png")
        logo = prepare_logo(logo_image, qr_image.size)
    except FileNotFoundError:
        st.error("Logo file not found. Please ensure 'logo.png' is in the same directory.")
        return None
    
    # Calculate dimensions
    padding = 40
    border_padding = 2
    font_size = 36  # Increased font size
    bottom_height = max(logo.size[1], font_size) + 30  # Increased bottom spacing
    
    # Create final image
    result = Image.new('RGBA', 
                      (qr_image.size[0] + padding * 2, 
                       qr_image.size[1] + padding * 2 + bottom_height),
                      (255, 255, 255, 255))
    
    # Paste QR code
    result.paste(qr_image, (padding, padding))
    
    # Add rectangular border in Leaf Space violet
    draw = ImageDraw.Draw(result)
    draw.rectangle(
        [padding - border_padding, 
         padding - border_padding, 
         padding + qr_image.size[0] + border_padding, 
         padding + qr_image.size[1] + border_padding],
        outline="#825DC7",
        width=2
    )
    
    # Prepare text
    try:
        font = ImageFont.truetype("arial.ttf", font_size)  # Using larger font size
    except OSError:
        font = ImageFont.load_default()
    
    text_width = draw.textlength(custom_text, font=font)
    
    # Calculate positions for logo and text
    bottom_y = padding + qr_image.size[1] + 25  # Space from QR code
    logo_x = padding  # Logo at left padding
    text_x = result.size[0] - padding - text_width  # Text aligned to right
    
    # Center text vertically with logo
    text_y = bottom_y + (logo.size[1] - font.size) // 2
    
    # Place logo and text
    result.paste(logo, (logo_x, bottom_y), logo)
    draw.text(
        (text_x, text_y),
        custom_text,
        font=font,
        fill="#825DC7"
    )
    
    return result

def main():
    """Main application function."""
    st.set_page_config(page_title="Leaf Space QR Code Generator", page_icon="🍃")
    st.title("Leaf Space QR Code Generator")
    
    url = st.text_input(
        "Enter the URL for the QR code:",
        "https://outlook.office365.com/owa/calendar/LeafSpaceSpaceTide1@leaf.space/bookings/"
    )
    
    custom_text = st.text_input(
        "Enter text to display below QR code:",
        "SCAN ME"
    )
    
    if st.button("Generate QR Code"):
        qr_image = generate_custom_qr_code(url, custom_text)
        if qr_image:
            st.image(qr_image, caption="Generated QR Code", use_container_width=True)
            
            # Prepare download
            buf = io.BytesIO()
            qr_image.save(buf, format="PNG")
            st.download_button(
                label="Download QR Code",
                data=buf.getvalue(),
                file_name=f"leafspace_qr_code_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                mime="image/png"
            )
    
    st.markdown("---")
    st.markdown("© 2025 Leaf Space. All rights reserved.")

if __name__ == "__main__":
    main()