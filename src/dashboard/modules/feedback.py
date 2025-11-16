"""
User Feedback Module for Steam Insights Dashboard.
Allows users to capture screenshots and submit feedback.
"""

import streamlit as st
from datetime import datetime
from pathlib import Path
import json
import base64
from PIL import Image


def save_feedback(feedback_text: str, screenshot_data: str = None, page_name: str = None):
    """
    Save user feedback to file with optional screenshot.
    
    Args:
        feedback_text: The feedback message
        screenshot_data: Base64 encoded screenshot (optional)
        page_name: Current page/stage name (optional)
    """
    # Create feedback directory if it doesn't exist
    feedback_dir = Path("data/feedback")
    feedback_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate timestamp-based filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save screenshot if provided
    screenshot_filename = None
    if screenshot_data:
        try:
            # Remove the data URL prefix if present
            if "base64," in screenshot_data:
                screenshot_data = screenshot_data.split("base64,")[1]
            
            # Decode and save screenshot
            screenshot_bytes = base64.b64decode(screenshot_data)
            screenshot_filename = f"screenshot_{timestamp}.png"
            screenshot_path = feedback_dir / screenshot_filename
            
            with open(screenshot_path, "wb") as f:
                f.write(screenshot_bytes)
        except Exception as e:
            st.error(f"Failed to save screenshot: {e}")
            screenshot_filename = None
    
    # Create feedback entry
    feedback_entry = {
        "timestamp": datetime.now().isoformat(),
        "page": page_name or "Unknown",
        "feedback": feedback_text,
        "screenshot": screenshot_filename,
        "user_agent": st.get_option("browser.serverAddress")
    }
    
    # Save to JSON file
    feedback_file = feedback_dir / f"feedback_{timestamp}.json"
    with open(feedback_file, "w") as f:
        json.dump(feedback_entry, f, indent=2)
    
    return True


def show_feedback_widget():
    """Display the feedback submission widget."""
    st.markdown("### 💬 Submit Feedback")
    st.info("💡 **Tip:** Close this form, take a screenshot with your OS tool (Win+Shift+S on Windows), then reopen and upload it below.")
    
    # Get current page context from session state
    current_page = st.session_state.get('dev_stage_selector', 'Unknown')
    
    with st.form("feedback_form", clear_on_submit=True):
        # Feedback text area
        feedback_text = st.text_area(
            "Your Feedback",
            placeholder="Share your thoughts, report bugs, or suggest features",
            height=120,
            help="Tell us what's on your mind!"
        )
        
        # Screenshot options
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📸 Screenshot (Optional)**")
            screenshot_file = st.file_uploader(
                "Upload screenshot",
                type=["png", "jpg", "jpeg"],
                help="Upload an image",
                label_visibility="collapsed"
            )
        
        with col2:
            st.markdown("**✉️ Email (Optional)**")
            contact_email = st.text_input(
                "Email",
                placeholder="your@email.com",
                help="For follow-up",
                label_visibility="collapsed"
            )
        
        st.markdown("---")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            submitted = st.form_submit_button(
                "📤 Submit",
                use_container_width=True,
                type="primary"
            )
        with col2:
            cancel = st.form_submit_button(
                "❌ Cancel",
                use_container_width=True
            )
        
        if cancel:
            st.session_state.show_feedback_modal = False
            st.rerun()
        
        if submitted:
            if not feedback_text.strip():
                st.error("⚠️ Please enter feedback before submitting.")
            else:
                # Save feedback
                try:
                    feedback_dir = Path("data/feedback")
                    feedback_dir.mkdir(parents=True, exist_ok=True)
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    # Save screenshot if provided
                    screenshot_filename = None
                    if screenshot_file is not None:
                        screenshot_filename = f"screenshot_{timestamp}.png"
                        screenshot_path = feedback_dir / screenshot_filename
                        screenshot_file.seek(0)
                        image = Image.open(screenshot_file)
                        image.save(screenshot_path, "PNG")
                    
                    # Create feedback entry
                    feedback_entry = {
                        "timestamp": datetime.now().isoformat(),
                        "page": current_page,
                        "feedback": feedback_text,
                        "screenshot": screenshot_filename,
                        "email": contact_email.strip() if contact_email else None
                    }
                    
                    # Save to JSON file
                    feedback_file = feedback_dir / f"feedback_{timestamp}.json"
                    with open(feedback_file, "w") as f:
                        json.dump(feedback_entry, f, indent=2)
                    
                    st.success("✅ Feedback submitted successfully!")
                    st.balloons()
                    st.session_state.show_feedback_modal = False
                    
                except Exception as e:
                    st.error(f"❌ Failed to save: {e}")
                    st.write("Please try again.")


def show_feedback_button():
    """Show feedback button in navigation bar."""
    # Initialize session state
    if 'show_feedback_modal' not in st.session_state:
        st.session_state.show_feedback_modal = False
    
    # Simple feedback button
    if st.button("💬", key="feedback_btn", help="Send Feedback"):
        st.session_state.show_feedback_modal = \
            not st.session_state.show_feedback_modal
        st.rerun()


def render_feedback_modal():
    """Render feedback modal if active."""
    if st.session_state.get('show_feedback_modal', False):
        with st.expander("💬 Submit Feedback", expanded=True):
            show_feedback_widget()


def show_feedback_management():
    """Admin view to see all submitted feedback."""
    st.markdown("### 📬 Feedback Management")
    st.markdown("Review all user feedback and screenshots")
    
    feedback_dir = Path("data/feedback")
    
    if not feedback_dir.exists():
        st.info("📭 No feedback has been submitted yet.")
        return
    
    # Get all feedback files
    feedback_files = sorted(feedback_dir.glob("feedback_*.json"), reverse=True)
    
    if not feedback_files:
        st.info("📭 No feedback has been submitted yet.")
        return
    
    st.markdown(f"**Total Feedback Items:** {len(feedback_files)}")
    st.markdown("---")
    
    # Display feedback items
    for feedback_file in feedback_files:
        with open(feedback_file, "r") as f:
            feedback_data = json.load(f)
        
        with st.expander(
            f"📝 {feedback_data.get('timestamp', 'Unknown')} - {feedback_data.get('page', 'Unknown')}"
        ):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("**Feedback:**")
                st.write(feedback_data.get('feedback', 'No feedback text'))
                
                if feedback_data.get('email'):
                    st.markdown(f"**Contact:** {feedback_data['email']}")
            
            with col2:
                st.markdown("**Details:**")
                st.write(f"📅 {feedback_data.get('timestamp', 'Unknown')}")
                st.write(f"📄 {feedback_data.get('page', 'Unknown')}")
                
                # Show screenshot if available
                if feedback_data.get('screenshot'):
                    screenshot_path = feedback_dir / feedback_data['screenshot']
                    if screenshot_path.exists():
                        st.markdown("**Screenshot:**")
                        st.image(str(screenshot_path))
            
            st.markdown("---")
